from .models import Notification
from .emails import send_application_received_email, send_status_update_email


STATUS_LABELS = {
    'applied': 'Applied',
    'under_review': 'Under Review',
    'shortlisted': 'Shortlisted',
    'shortlised': 'Shortlisted',
    'interview_scheduled': 'Interview Scheduled',
    'rejected': 'Rejected',
    'hired': 'Hired',
    'withdrawn': 'Withdrawn',
}


def create_notification(user, title, message, notification_type='general'):
    """Safely creates a Notification record for the target user."""
    if not user:
        return None
    return Notification.objects.create(
        user=user,
        title=title[:255],
        message=message,
        notification_type=notification_type,
    )


def notify_for_status_history(history):
    """
    Creates the appropriate Notification when an ApplicationStatusHistory record is logged.
    - New submission ('applied' with empty old_status) -> notifies the posting employer.
    - Withdrawal ('withdrawn') -> notifies the posting employer.
    - Interview scheduled ('interview_scheduled') -> notifies the applicant with type 'interview_scheduled'.
    - Other pipeline status changes -> notifies the applicant with type 'application_update'.
    """
    application = history.application
    job = application.job
    company_name = job.company.name if job.company else 'Employer'
    applicant_user = application.applicant.user if application.applicant else None
    employer_user = job.posted_by.user if job.posted_by else None
    new_status = history.new_status

    if new_status == 'applied' and not history.old_status:
        send_application_received_email(application)
        if employer_user:
            return create_notification(
                user=employer_user,
                title=f"New Application: {job.title}",
                message=f"{application.applicant.full_name} applied for {job.title} at {company_name}.",
                notification_type='application_update',
            )
        return None

    if new_status == 'withdrawn':
        send_status_update_email(application, history.old_status, 'withdrawn', history.notes)
        if employer_user:
            return create_notification(
                user=employer_user,
                title=f"Application Withdrawn: {job.title}",
                message=f"{application.applicant.full_name} withdrew their application for {job.title}.",
                notification_type='application_update',
            )
        return None

    if not applicant_user:
        return None

    if new_status == 'interview_scheduled':
        # When created via interview_create_view, the rich .ics invite is dispatched directly there.
        if history.notes != 'Interview Scheduled.':
            send_status_update_email(application, history.old_status, new_status, history.notes)
        return create_notification(
            user=applicant_user,
            title=f"Interview Scheduled: {job.title}",
            message=f"Your interview for {job.title} at {company_name} has been scheduled.",
            notification_type='interview_scheduled',
        )

    send_status_update_email(application, history.old_status, new_status, history.notes)
    friendly_status = STATUS_LABELS.get(new_status, new_status.replace('_', ' ').title())
    return create_notification(
        user=applicant_user,
        title=f"Application Update: {job.title}",
        message=f"Your application for {job.title} at {company_name} is now '{friendly_status}'.",
        notification_type='application_update',
    )
