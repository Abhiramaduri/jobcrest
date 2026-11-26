import os
import uuid
import mimetypes
from django.shortcuts import render
from django.http import FileResponse
from django.core.signing import BadSignature, SignatureExpired
from rest_framework.decorators import api_view, permission_classes, parser_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings as django_settings
from django.core.files.storage import default_storage
from .models import User, JobSeekerProfile, Skill, JobSeekerSkill, Education, Experience, OTPVerification
from .resume_security import verify_signed_resume_token
from .validators import validate_resume_file
from .lookup import get_object_by_uuid_or_id
from .throttles import (
    LoginRateThrottle, RegisterRateThrottle, PasswordResetRateThrottle,
    OTPRateThrottle, get_client_ip, is_account_locked, record_failed_attempt,
    clear_failed_attempts, LOCKOUT_THRESHOLD
)
from notifications.emails import (
    send_otp_email_message,
    send_verify_email,
    send_welcome_email,
    verify_email_token,
)
from rest_framework import status

from .serializers import (
    RegisterSerializer, UserSerilizer, JobSeekerProfileSerializer,
    SkillSerializer, JobSeekerSkillSerializer, EducationSerializer, ExperienceSerializer
)
from .permissions import isJobSeeker


# ─────────────────────────────────────────────────────────
# EMAIL HELPER
# ─────────────────────────────────────────────────────────

def send_otp_email(email, otp_code, purpose):
    send_otp_email_message(email=email, otp_code=otp_code, purpose=purpose, fail_silently=False)


# ─────────────────────────────────────────────────────────
# STEP 1 — SEND REGISTRATION OTP
# ─────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPRateThrottle, RegisterRateThrottle])
def send_registration_otp_view(request):
    email = request.data.get('email', '').strip()
    if not email:
        return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'detail': 'An account with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    otp_obj = OTPVerification.generate_otp(email=email, purpose='registration')
    try:
        send_otp_email(email, otp_obj.otp, purpose='registration')
    except Exception as e:
        return Response({'detail': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'detail': 'OTP sent to your email. It expires in 10 minutes.'}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────
# STEP 2 — VERIFY OTP + REGISTER USER
# ─────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegisterRateThrottle, OTPRateThrottle])
def register_view(request):
    email = request.data.get('email', '').strip()
    otp_code = request.data.get('otp', '').strip()

    if not otp_code:
        return Response({'detail': 'OTP is required.'}, status=status.HTTP_400_BAD_REQUEST)

    otp_obj = OTPVerification.objects.filter(
        email=email, purpose='registration', is_used=False
    ).order_by('-created_at').first()

    if not otp_obj:
        return Response({'detail': 'No OTP found for this email. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
    if otp_obj.is_expired():
        return Response({'detail': 'OTP has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
    if otp_obj.otp != otp_code:
        return Response({'detail': 'Incorrect OTP. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        # Return first field error as a readable detail message
        errors = serializer.errors
        first_key = next(iter(errors))
        first_msg = errors[first_key][0] if isinstance(errors[first_key], list) else str(errors[first_key])
        return Response({'detail': f'{first_key}: {first_msg}'}, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    user.is_verified = True
    user.save()

    otp_obj.is_used = True
    otp_obj.save()

    send_welcome_email(user)

    refresh = RefreshToken.for_user(user)
    return Response({
        "user": UserSerilizer(user).data,
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────────────────────────
# VERIFY EMAIL (SIGNED LINK FLOW)
# ─────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([OTPRateThrottle])
def send_verification_email_view(request):
    user = request.user
    if user.is_verified:
        return Response({'detail': 'Email address is already verified.'}, status=status.HTTP_400_BAD_REQUEST)
    if not user.email:
        return Response({'detail': 'No email address associated with this account.'}, status=status.HTTP_400_BAD_REQUEST)

    send_verify_email(user, request=request, fail_silently=True)
    return Response({'detail': 'Verification email sent.'}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPRateThrottle])
def verify_email_view(request):
    token = request.query_params.get('token') if request.method == 'GET' else request.data.get('token')
    if not token:
        return Response({'detail': 'Verification token is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_id, email = verify_email_token(token)
    except SignatureExpired:
        return Response({'detail': 'Verification link has expired.'}, status=status.HTTP_400_BAD_REQUEST)
    except (BadSignature, ValueError):
        return Response({'detail': 'Invalid verification token.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(pk=user_id, email=email).first()
    if not user:
        return Response({'detail': 'User account not found.'}, status=status.HTTP_404_NOT_FOUND)

    if not user.is_verified:
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        send_welcome_email(user)

    return Response({'detail': 'Email verified successfully.'}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login_view(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    client_ip = get_client_ip(request)

    if not username or not password:
        return Response({'detail': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Check for active temporary lockout
    locked, remaining = is_account_locked(username, client_ip)
    if locked:
        mins = max(1, remaining // 60)
        return Response(
            {'detail': f'Account temporarily locked due to too many failed login attempts. Please try again in {mins} minute(s).'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    user = authenticate(username=username, password=password)
    if user is None:
        locked, attempts, remaining = record_failed_attempt(username, client_ip)
        if locked:
            mins = max(1, remaining // 60)
            return Response(
                {'detail': f'Too many failed login attempts. Your account has been temporarily locked for {mins} minutes.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        remaining_attempts = max(0, LOCKOUT_THRESHOLD - attempts)
        return Response(
            {'detail': f'Invalid credentials. {remaining_attempts} attempt(s) remaining before temporary lockout.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Clear failed attempt counters on successful login
    clear_failed_attempts(username, client_ip)

    refresh = RefreshToken.for_user(user)
    return Response({
        "user": UserSerilizer(user).data,
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    })


# ─────────────────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    refresh_token = request.data.get("refresh")
    if not refresh_token or not isinstance(refresh_token, str):
        return Response(
            {"detail": "A valid refresh token is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
    except TokenError:
        return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────────────────
# ME
# ─────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(UserSerilizer(request.user).data)


# ─────────────────────────────────────────────────────────
# FORGOT PASSWORD — STEP 1: SEND OTP
# ─────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetRateThrottle])
def password_reset_request_view(request):
    email = request.data.get('email', '').strip()
    if not email:
        return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Always return success even if no account to prevent user enumeration
    user = User.objects.filter(email=email).first()
    if user:
        otp_obj = OTPVerification.generate_otp(email=email, purpose='password_reset')
        try:
            send_otp_email(email, otp_obj.otp, purpose='password_reset')
        except Exception as e:
            return Response({'detail': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'detail': 'If an account with that email exists, an OTP has been sent.'}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────
# FORGOT PASSWORD — STEP 2: VERIFY OTP
# ─────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPRateThrottle, PasswordResetRateThrottle])
def password_reset_verify_otp_view(request):
    email = request.data.get('email', '').strip()
    otp_code = request.data.get('otp', '').strip()

    if not email or not otp_code:
        return Response({'detail': 'Email and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

    otp_obj = OTPVerification.objects.filter(
        email=email, purpose='password_reset', is_used=False
    ).order_by('-created_at').first()

    if not otp_obj:
        return Response({'detail': 'No OTP found. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
    if otp_obj.is_expired():
        return Response({'detail': 'OTP has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
    if otp_obj.otp != otp_code:
        return Response({'detail': 'Incorrect OTP. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'detail': 'OTP verified. You may now reset your password.'}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────
# FORGOT PASSWORD — STEP 3: SET NEW PASSWORD
# ─────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetRateThrottle])
def password_reset_confirm_view(request):
    email = request.data.get('email', '').strip()
    otp_code = request.data.get('otp', '').strip()
    new_password = request.data.get('new_password', '')
    confirm_password = request.data.get('confirm_password', '')

    if not all([email, otp_code, new_password, confirm_password]):
        return Response({'detail': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if new_password != confirm_password:
        return Response({'detail': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

    otp_obj = OTPVerification.objects.filter(
        email=email, purpose='password_reset', is_used=False
    ).order_by('-created_at').first()

    if not otp_obj:
        return Response({'detail': 'Invalid or expired OTP. Please restart the process.'}, status=status.HTTP_400_BAD_REQUEST)
    if otp_obj.is_expired():
        return Response({'detail': 'OTP has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
    if otp_obj.otp != otp_code:
        return Response({'detail': 'Incorrect OTP.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(new_password)
    except DjangoValidationError as e:
        return Response({'detail': ' '.join(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=email).first()
    if not user:
        return Response({'detail': 'No account found with this email.'}, status=status.HTTP_404_NOT_FOUND)

    user.set_password(new_password)
    user.save()

    otp_obj.is_used = True
    otp_obj.save()

    return Response({'detail': 'Password reset successfully. You can now log in.'}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────
# JOB SEEKER PROFILE & SECURE CANDIDATE ACCESS
# ─────────────────────────────────────────────────────────

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated, isJobSeeker])
def jobseeker_profile_view(request):
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    if request.method == 'GET':
        return Response(JobSeekerProfileSerializer(profile, context={'request': request}).data)
    partial = request.method == 'PATCH'
    serializer = JobSeekerProfileSerializer(profile, data=request.data, partial=partial, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, isJobSeeker])
@parser_classes([MultiPartParser, FormParser])
def jobseeker_resume_upload_view(request):
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    resume_file = request.FILES.get('resume')
    if not resume_file:
        return Response({'detail': 'No resume file provided.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_resume_file(resume_file)
    except DjangoValidationError as exc:
        message = exc.messages[0] if hasattr(exc, 'messages') and exc.messages else str(exc)
        return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)

    # Safely clean up previous resume file if replacing to avoid orphaned files in cloud/local storage
    if profile.resume:
        try:
            profile.resume.delete(save=False)
        except Exception:
            pass

    profile.resume = resume_file
    profile.save()
    return Response(JobSeekerProfileSerializer(profile, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def public_jobseeker_profile_view(request, identifier):
    """
    Candidate Profile Access Endpoint.
    
    Security & Privacy Controls:
    1. Lookups are handled via UUID (unguessable, preventing sequential ID enumeration / scraping).
    2. Strict Authorization:
       - The profile owner (candidate themselves)
       - An employer who has received an application from this candidate
       - Staff / superusers
       All other users (including other candidates / arbitrary employers) are denied with HTTP 403.
    """
    profile = None
    identifier_str = str(identifier).strip()

    # Attempt lookup via UUID
    try:
        val = uuid.UUID(identifier_str)
        profile = JobSeekerProfile.objects.filter(uuid=val).first()
    except (ValueError, AttributeError):
        pass

    # Optional integer fallback for internal backward compatibility
    if not profile and identifier_str.isdigit():
        profile = JobSeekerProfile.objects.filter(id=int(identifier_str)).first()

    if not profile:
        return Response({'detail': 'Candidate profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    # 1. Staff / Superuser check
    is_staff = request.user.is_staff or request.user.is_superuser

    # 2. Owner check
    is_owner = (profile.user == request.user)

    # 3. Employer with application check
    is_authorized_employer = False
    if hasattr(request.user, 'employer_profile') or getattr(request.user, 'user_type', None) == 'employer':
        employer_profile = getattr(request.user, 'employer_profile', None)
        if employer_profile:
            from applications.models import Application
            from django.db.models import Q
            is_authorized_employer = Application.objects.filter(
                applicant=profile
            ).filter(
                Q(job__posted_by=employer_profile) |
                Q(job__company=employer_profile.company)
            ).exists()

    if not (is_staff or is_owner or is_authorized_employer):
        return Response(
            {'detail': 'You do not have permission to view this candidate profile.'},
            status=status.HTTP_403_FORBIDDEN
        )

    return Response(JobSeekerProfileSerializer(profile, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def resume_download_view(request):
    """
    Serves candidate resumes through signed, expiring tokens.
    Protects against unauthorized direct access, enumeration, and path traversal.
    Uses default_storage abstraction for seamless operation across local disk,
    S3, Supabase Storage, and other cloud providers.
    """
    token = request.query_params.get('token')
    if not token:
        return Response({'detail': 'Signed token is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        relative_path = verify_signed_resume_token(token)
    except SignatureExpired:
        return Response({'detail': 'This resume download link has expired.'}, status=status.HTTP_403_FORBIDDEN)
    except BadSignature:
        return Response({'detail': 'Invalid or tampered resume link.'}, status=status.HTTP_403_FORBIDDEN)

    # Path traversal protection
    normalized_rel = os.path.normpath(relative_path).replace('\\', '/').lstrip('/')
    if '..' in normalized_rel.split('/'):
        return Response({'detail': 'Invalid file path.'}, status=status.HTTP_400_BAD_REQUEST)

    if not default_storage.exists(normalized_rel):
        return Response({'detail': 'Resume file not found.'}, status=status.HTTP_404_NOT_FOUND)

    content_type, _ = mimetypes.guess_type(normalized_rel)
    if not content_type:
        content_type = 'application/pdf'

    filename = os.path.basename(normalized_rel)
    file_obj = default_storage.open(normalized_rel, 'rb')
    response = FileResponse(file_obj, content_type=content_type)
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


# ─────────────────────────────────────────────────────────
# EDUCATION
# ─────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, isJobSeeker])
def education_list_create_view(request):
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    if request.method == 'GET':
        return Response(EducationSerializer(Education.objects.filter(jobseeker=profile), many=True).data)
    serializer = EducationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(jobseeker=profile)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, isJobSeeker])
def education_detail_view(request, pk):
    education = get_object_by_uuid_or_id(Education.objects.filter(jobseeker__user=request.user), pk)
    if request.method == 'GET':
        return Response(EducationSerializer(education).data)
    if request.method == 'DELETE':
        education.delete()
        return Response({"message": "Education deleted"}, status=status.HTTP_204_NO_CONTENT)
    partial = request.method == 'PATCH'
    serializer = EducationSerializer(education, data=request.data, partial=partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


# ─────────────────────────────────────────────────────────
# EXPERIENCE
# ─────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, isJobSeeker])
def experience_list_create_view(request):
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    if request.method == 'GET':
        return Response(ExperienceSerializer(Experience.objects.filter(jobseeker=profile), many=True).data)
    serializer = ExperienceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(jobseeker=profile)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, isJobSeeker])
def experience_detail_view(request, pk):
    experience = get_object_by_uuid_or_id(Experience.objects.filter(jobseeker__user=request.user), pk)
    if request.method == 'GET':
        return Response(ExperienceSerializer(experience).data)
    if request.method == 'DELETE':
        experience.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    partial = request.method == 'PATCH'
    serializer = ExperienceSerializer(experience, data=request.data, partial=partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


# ─────────────────────────────────────────────────────────
# SKILLS
# ─────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, isJobSeeker])
def skill_list_create_view(request):
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    if request.method == 'GET':
        return Response(JobSeekerSkillSerializer(JobSeekerSkill.objects.filter(jobseeker=profile), many=True).data)
    serializer = JobSeekerSkillSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(jobseeker=profile)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, isJobSeeker])
def skill_delete_view(request, pk):
    skill = get_object_by_uuid_or_id(JobSeekerSkill.objects.filter(jobseeker__user=request.user), pk)
    skill.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def all_skills_list_view(request):
    return Response(SkillSerializer(Skill.objects.all(), many=True).data)


# ─────────────────────────────────────────────────────────
# LOAD BALANCER HEALTH CHECK
# ─────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([])  # Explicitly unthrottled for load balancer liveness & readiness probes
def health_check_view(request):
    """
    Health check endpoint for Load Balancers (Render, Nginx, AWS ALB, Kubernetes).
    Validates database connectivity and returns HTTP 200 OK or 503 if degraded.
    """
    from django.db import connection
    db_ok = True
    try:
        connection.ensure_connection()
    except Exception:
        db_ok = False

    data = {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "service": "jobcrest-api",
    }
    return Response(data, status=status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE)

