import logging
from datetime import timedelta, timezone as dt_timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.utils import timezone
from django.utils.html import escape

logger = logging.getLogger(__name__)

EMAIL_VERIFY_SALT = 'jobcrest.email.verify.v1'
EMAIL_VERIFY_MAX_AGE_SECONDS = 86400  # 24 hours

STATUS_DISPLAY_LABELS = {
    'applied': 'Applied',
    'under_review': 'Under Review',
    'shortlisted': 'Shortlisted',
    'shortlised': 'Shortlisted',
    'interview_scheduled': 'Interview Scheduled',
    'rejected': 'Rejected',
    'hired': 'Hired / Offer Extended',
    'withdrawn': 'Withdrawn',
}


def _wrap_html_email(heading, body_html):
    """Wraps transactional email content in a consistent JobCrest HTML shell."""
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#FAF8F5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#2D2426;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="padding:32px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="max-width:600px;width:100%;background:#FFFFFF;border:1px solid #E8DFD5;border-radius:16px;overflow:hidden;">
          <tr>
            <td style="background:#5E1D2F;padding:24px 32px;">
              <span style="font-size:20px;font-weight:700;color:#FAF8F5;letter-spacing:-0.02em;">JobCrest</span>
              <p style="margin:6px 0 0;font-size:13px;color:#F3DCE1;">{escape(heading)}</p>
            </td>
          </tr>
          <tr>
            <td style="padding:28px 32px;font-size:14px;line-height:1.6;color:#3A3032;">
              {body_html}
            </td>
          </tr>
          <tr>
            <td style="padding:18px 32px;background:#FAF8F5;border-top:1px solid #E8DFD5;font-size:12px;color:#7A6C6F;">
              Sent by <a href="{escape(frontend_url)}" style="color:#5E1D2F;text-decoration:none;font-weight:600;">JobCrest</a> &middot; Curated Career Marketplace
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _send_email_message(subject, text_body, html_body, recipient_list, attachments=None, fail_silently=True):
    """Dispatches a multipart email with optional attachments via the configured Django email backend."""
    recipients = [addr.strip() for addr in (recipient_list or []) if addr and addr.strip()]
    if not recipients:
        return False

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
    )
    if html_body:
        msg.attach_alternative(html_body, 'text/html')
    if attachments:
        for filename, content, mimetype in attachments:
            msg.attach(filename, content, mimetype)

    try:
        msg.send(fail_silently=False)
        return True
    except Exception as exc:
        logger.exception("Failed sending email '%s' to %s: %s", subject, recipients, exc)
        if not fail_silently:
            raise
        return False


def send_otp_email_message(email, otp_code, purpose, fail_silently=False):
    """Sends a 6-digit OTP email for registration verification or password reset."""
    if purpose == 'registration':
        subject = "Your JobCrest Email Verification Code"
        heading = "Verify your email address"
        intro = "Thank you for signing up for JobCrest! Enter the 6-digit verification code below to verify your email:"
        outro = "This code expires in 10 minutes. If you did not create an account, you can safely ignore this message."
    else:
        subject = "Your JobCrest Password Reset Code"
        heading = "Password reset verification"
        intro = "We received a request to reset your JobCrest password. Enter the 6-digit code below to continue:"
        outro = "This code expires in 10 minutes. If you did not request a password reset, no action is needed."

    text_body = f"Hello,\n\n{intro}\n\n    {otp_code}\n\n{outro}\n\n— The JobCrest Team\n"
    html_body = _wrap_html_email(
        heading,
        f"<p>Hello,</p><p>{escape(intro)}</p>"
        f"<div style=\"margin:20px 0;padding:16px 24px;background:#FAF8F5;border:1px solid #E8DFD5;border-radius:12px;text-align:center;\">"
        f"<span style=\"font-size:28px;font-weight:800;letter-spacing:6px;color:#5E1D2F;\">{escape(str(otp_code))}</span></div>"
        f"<p style=\"color:#6E6265;font-size:13px;\">{escape(outro)}</p>",
    )
    return _send_email_message(subject, text_body, html_body, [email], fail_silently=fail_silently)


def generate_email_verification_token(user):
    """Generates a signed, expiring token encoding user ID and email address."""
    signer = TimestampSigner(salt=EMAIL_VERIFY_SALT)
    return signer.sign(f"{user.pk}:{user.email}")


def verify_email_token(token, max_age=EMAIL_VERIFY_MAX_AGE_SECONDS):
    """
    Validates a signed email verification token and returns (user_id, email).
    Raises SignatureExpired or BadSignature on invalid/expired tokens.
    """
    if not token:
        raise BadSignature("Verification token is required.")
    signer = TimestampSigner(salt=EMAIL_VERIFY_SALT)
    raw = signer.unsign(token, max_age=max_age)
    user_id_str, email = raw.split(':', 1)
    return int(user_id_str), email


def send_verify_email(user, request=None, fail_silently=True):
    """Sends a signed email verification link to the user."""
    if not user or not user.email:
        return False
    token = generate_email_verification_token(user)
    relative_path = f"/api/auth/verify-email/?token={token}"
    if request is not None:
        try:
            verify_url = request.build_absolute_uri(relative_path)
        except Exception:
            verify_url = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')}/verify-email?token={token}"
    else:
        verify_url = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')}/verify-email?token={token}"

    subject = "Verify Your JobCrest Email Address"
    text_body = (
        f"Hello {user.username},\n\n"
        f"Please verify your email address by visiting the link below (valid for 24 hours):\n"
        f"{verify_url}\n\n"
        f"— The JobCrest Team\n"
    )
    html_body = _wrap_html_email(
        "Email Verification",
        f"<p>Hello <strong>{escape(user.username)}</strong>,</p>"
        f"<p>Please confirm your email address to activate all features on your JobCrest account.</p>"
        f"<p style=\"margin:24px 0;\"><a href=\"{escape(verify_url)}\" style=\"display:inline-block;padding:12px 24px;background:#5E1D2F;color:#FFFFFF;text-decoration:none;border-radius:10px;font-weight:600;\">Verify Email Address</a></p>"
        f"<p style=\"font-size:12px;color:#7A6C6F;\">This verification link expires in 24 hours. Or copy this URL: {escape(verify_url)}</p>",
    )
    return _send_email_message(subject, text_body, html_body, [user.email], fail_silently=fail_silently)


def send_welcome_email(user, fail_silently=True):
    """Sends a welcome email after successful account registration."""
    if not user or not user.email:
        return False

    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    is_employer = getattr(user, 'user_type', '') == 'employer'
    cta_url = f"{frontend_url}/employer/dashboard" if is_employer else f"{frontend_url}/jobs"
    cta_label = "Go to Employer Dashboard" if is_employer else "Explore Open Roles"
    role_summary = (
        "Set up your company profile, post openings, and manage candidate pipelines effortlessly."
        if is_employer
        else "Complete your profile, upload your resume, and apply to curated career opportunities."
    )

    subject = f"Welcome to JobCrest, {user.username}!"
    text_body = (
        f"Welcome to JobCrest, {user.username}!\n\n"
        f"Your account is verified and ready. {role_summary}\n\n"
        f"Get started here: {cta_url}\n\n"
        f"— The JobCrest Team\n"
    )
    html_body = _wrap_html_email(
        "Welcome to JobCrest",
        f"<p>Welcome aboard, <strong>{escape(user.username)}</strong>!</p>"
        f"<p>Your JobCrest account has been verified and activated.</p>"
        f"<p>{escape(role_summary)}</p>"
        f"<p style=\"margin:24px 0;\"><a href=\"{escape(cta_url)}\" style=\"display:inline-block;padding:12px 24px;background:#5E1D2F;color:#FFFFFF;text-decoration:none;border-radius:10px;font-weight:600;\">{escape(cta_label)}</a></p>",
    )
    return _send_email_message(subject, text_body, html_body, [user.email], fail_silently=fail_silently)


def send_application_received_email(application, fail_silently=True):
    """Sends confirmation email to the applicant and an alert email to the posting employer."""
    job = application.job
    company_name = job.company.name if job.company else 'Employer'
    applicant_user = application.applicant.user if application.applicant else None
    employer_user = job.posted_by.user if job.posted_by else None
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')

    sent_any = False
    if applicant_user and applicant_user.email:
        subject = f"Application Received: {job.title} at {company_name}"
        text_body = (
            f"Hello {application.applicant.full_name},\n\n"
            f"We have received your application for {job.title} at {company_name}.\n"
            f"You can track your application progress anytime at: {frontend_url}/applications\n\n"
            f"— The JobCrest Team\n"
        )
        html_body = _wrap_html_email(
            "Application Confirmed",
            f"<p>Hello <strong>{escape(application.applicant.full_name)}</strong>,</p>"
            f"<p>Your application for <strong>{escape(job.title)}</strong> at <strong>{escape(company_name)}</strong> has been successfully received.</p>"
            f"<p style=\"margin:24px 0;\"><a href=\"{escape(frontend_url)}/applications\" style=\"display:inline-block;padding:12px 24px;background:#5E1D2F;color:#FFFFFF;text-decoration:none;border-radius:10px;font-weight:600;\">Track Application</a></p>",
        )
        sent_any = _send_email_message(subject, text_body, html_body, [applicant_user.email], fail_silently=fail_silently) or sent_any

    if employer_user and employer_user.email:
        subject = f"New Application Received: {job.title}"
        text_body = (
            f"Hello {employer_user.username},\n\n"
            f"{application.applicant.full_name} just applied for your '{job.title}' posting.\n"
            f"Review candidate pipeline: {frontend_url}/employer/jobs\n\n"
            f"— The JobCrest Team\n"
        )
        html_body = _wrap_html_email(
            "New Candidate Application",
            f"<p>Hello <strong>{escape(employer_user.username)}</strong>,</p>"
            f"<p><strong>{escape(application.applicant.full_name)}</strong> has submitted an application for <strong>{escape(job.title)}</strong>.</p>"
            f"<p style=\"margin:24px 0;\"><a href=\"{escape(frontend_url)}/employer/jobs\" style=\"display:inline-block;padding:12px 24px;background:#5E1D2F;color:#FFFFFF;text-decoration:none;border-radius:10px;font-weight:600;\">Review Candidate</a></p>",
        )
        sent_any = _send_email_message(subject, text_body, html_body, [employer_user.email], fail_silently=fail_silently) or sent_any

    return sent_any


def send_status_update_email(application, old_status, new_status, notes='', fail_silently=True):
    """Notifies the applicant (or employer on withdrawal) about an application stage transition."""
    job = application.job
    company_name = job.company.name if job.company else 'Employer'
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')

    if new_status == 'withdrawn':
        employer_user = job.posted_by.user if job.posted_by else None
        if not employer_user or not employer_user.email:
            return False
        subject = f"Application Withdrawn: {job.title}"
        text_body = (
            f"Hello {employer_user.username},\n\n"
            f"{application.applicant.full_name} has withdrawn their application for {job.title}.\n\n"
            f"— The JobCrest Team\n"
        )
        html_body = _wrap_html_email(
            "Application Withdrawn",
            f"<p>Hello <strong>{escape(employer_user.username)}</strong>,</p>"
            f"<p><strong>{escape(application.applicant.full_name)}</strong> withdrew their application for <strong>{escape(job.title)}</strong>.</p>",
        )
        return _send_email_message(subject, text_body, html_body, [employer_user.email], fail_silently=fail_silently)

    applicant_user = application.applicant.user if application.applicant else None
    if not applicant_user or not applicant_user.email:
        return False

    friendly_status = STATUS_DISPLAY_LABELS.get(new_status, new_status.replace('_', ' ').title())
    notes_text = f"\nNote from employer: {notes}\n" if notes else ""
    notes_html = (
        f"<div style=\"margin:16px 0;padding:12px 16px;background:#FAF8F5;border-left:3px solid #5E1D2F;font-size:13px;\">"
        f"<strong>Note:</strong> {escape(notes)}</div>"
        if notes else ""
    )

    subject = f"Application Status Update: {job.title} ({friendly_status})"
    text_body = (
        f"Hello {application.applicant.full_name},\n\n"
        f"Your application status for {job.title} at {company_name} has been updated to: {friendly_status}.\n"
        f"{notes_text}\n"
        f"View details: {frontend_url}/applications\n\n"
        f"— The JobCrest Team\n"
    )
    html_body = _wrap_html_email(
        "Application Status Update",
        f"<p>Hello <strong>{escape(application.applicant.full_name)}</strong>,</p>"
        f"<p>Your application for <strong>{escape(job.title)}</strong> at <strong>{escape(company_name)}</strong> is now marked as "
        f"<strong style=\"color:#5E1D2F;\">{escape(friendly_status)}</strong>.</p>"
        f"{notes_html}"
        f"<p style=\"margin:24px 0;\"><a href=\"{escape(frontend_url)}/applications\" style=\"display:inline-block;padding:12px 24px;background:#5E1D2F;color:#FFFFFF;text-decoration:none;border-radius:10px;font-weight:600;\">View Applications</a></p>",
    )
    return _send_email_message(subject, text_body, html_body, [applicant_user.email], fail_silently=fail_silently)


def _escape_ics_text(value):
    """Escapes special characters according to RFC 5545 text rules."""
    text = str(value or '')
    return (
        text.replace('\\', '\\\\')
        .replace(';', '\\;')
        .replace(',', '\\,')
        .replace('\r\n', '\\n')
        .replace('\n', '\\n')
    )


def build_interview_ics(interview):
    """Builds an RFC 5545 compliant iCalendar (.ics) event payload for an Interview."""
    application = interview.application
    job = application.job
    company_name = job.company.name if job.company else 'JobCrest Employer'
    employer_email = (job.posted_by.user.email if job.posted_by and job.posted_by.user else '') or 'noreply@jobcrest.com'
    applicant_user = application.applicant.user if application.applicant else None
    applicant_email = (applicant_user.email if applicant_user else '') or ''
    applicant_name = application.applicant.full_name if application.applicant else 'Candidate'

    start_dt = interview.scheduled_at
    if timezone.is_naive(start_dt):
        start_dt = timezone.make_aware(start_dt, dt_timezone.utc)
    start_utc = start_dt.astimezone(dt_timezone.utc)
    end_utc = start_utc + timedelta(hours=1)
    now_utc = timezone.now().astimezone(dt_timezone.utc)

    fmt = '%Y%m%dT%H%M%SZ'
    mode_label = interview.mode.replace('_', ' ').title()
    location = interview.meeting_link or mode_label
    desc_parts = [f"Interview for {job.title} at {company_name}", f"Format: {mode_label}"]
    if interview.meeting_link:
        desc_parts.append(f"Join Link: {interview.meeting_link}")
    if interview.interview_notes:
        desc_parts.append(f"Notes: {interview.interview_notes}")
    description = "\n".join(desc_parts)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//JobCrest//Interview Scheduler//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:REQUEST",
        "BEGIN:VEVENT",
        f"UID:interview-{interview.uuid}@jobcrest.com",
        f"DTSTAMP:{now_utc.strftime(fmt)}",
        f"DTSTART:{start_utc.strftime(fmt)}",
        f"DTEND:{end_utc.strftime(fmt)}",
        f"SUMMARY:{_escape_ics_text(f'Interview: {job.title} at {company_name}')}",
        f"DESCRIPTION:{_escape_ics_text(description)}",
        f"LOCATION:{_escape_ics_text(location)}",
        f"ORGANIZER;CN={_escape_ics_text(company_name)}:mailto:{employer_email}",
    ]
    if applicant_email:
        lines.append(f"ATTENDEE;CN={_escape_ics_text(applicant_name)};RSVP=TRUE:mailto:{applicant_email}")
    lines.extend([
        "STATUS:CONFIRMED",
        "END:VEVENT",
        "END:VCALENDAR",
        "",
    ])
    return "\r\n".join(lines)


def send_interview_invite_email(interview, rescheduled=False, fail_silently=True):
    """Sends an interview invitation (or reschedule notice) with an .ics calendar attachment."""
    application = interview.application
    applicant_user = application.applicant.user if application.applicant else None
    if not applicant_user or not applicant_user.email:
        return False

    job = application.job
    company_name = job.company.name if job.company else 'Employer'
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')

    start_dt = interview.scheduled_at
    if timezone.is_naive(start_dt):
        start_dt = timezone.make_aware(start_dt, dt_timezone.utc)
    scheduled_str = start_dt.astimezone(dt_timezone.utc).strftime('%B %d, %Y at %H:%M UTC')
    mode_label = interview.mode.replace('_', ' ').title()

    action_word = "Rescheduled" if rescheduled else "Invitation"
    subject = f"Interview {action_word}: {job.title} at {company_name}"
    meeting_line = f"Meeting Link: {interview.meeting_link}\n" if interview.meeting_link else ""
    notes_line = f"Notes: {interview.interview_notes}\n" if interview.interview_notes else ""

    text_body = (
        f"Hello {application.applicant.full_name},\n\n"
        f"Your interview for {job.title} at {company_name} has been {'rescheduled' if rescheduled else 'scheduled'}.\n\n"
        f"Date & Time: {scheduled_str}\n"
        f"Mode: {mode_label}\n"
        f"{meeting_line}{notes_line}\n"
        f"A calendar invitation (.ics) is attached to this email.\n"
        f"View interviews: {frontend_url}/interviews\n\n"
        f"— The JobCrest Team\n"
    )
    meeting_html = (
        f"<p><strong>Meeting Link:</strong> <a href=\"{escape(interview.meeting_link)}\">{escape(interview.meeting_link)}</a></p>"
        if interview.meeting_link else ""
    )
    notes_html = (
        f"<p><strong>Notes:</strong> {escape(interview.interview_notes)}</p>"
        if interview.interview_notes else ""
    )
    html_body = _wrap_html_email(
        f"Interview {action_word}",
        f"<p>Hello <strong>{escape(application.applicant.full_name)}</strong>,</p>"
        f"<p>Your interview for <strong>{escape(job.title)}</strong> at <strong>{escape(company_name)}</strong> is {'rescheduled' if rescheduled else 'confirmed'}.</p>"
        f"<div style=\"margin:18px 0;padding:16px;background:#FAF8F5;border:1px solid #E8DFD5;border-radius:12px;\">"
        f"<p style=\"margin:0 0 6px;\"><strong>When:</strong> {escape(scheduled_str)}</p>"
        f"<p style=\"margin:0 0 6px;\"><strong>Format:</strong> {escape(mode_label)}</p>"
        f"{meeting_html}{notes_html}</div>"
        f"<p>A calendar invite (<code>interview-invite.ics</code>) is attached so you can add it straight to your calendar.</p>"
        f"<p style=\"margin:24px 0;\"><a href=\"{escape(frontend_url)}/interviews\" style=\"display:inline-block;padding:12px 24px;background:#5E1D2F;color:#FFFFFF;text-decoration:none;border-radius:10px;font-weight:600;\">View Interview Details</a></p>",
    )

    ics_payload = build_interview_ics(interview)
    attachments = [
        ('interview-invite.ics', ics_payload, 'text/calendar; method=REQUEST; charset=UTF-8'),
    ]
    return _send_email_message(
        subject,
        text_body,
        html_body,
        [applicant_user.email],
        attachments=attachments,
        fail_silently=fail_silently,
    )
