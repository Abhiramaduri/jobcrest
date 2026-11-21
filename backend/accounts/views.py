from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings as django_settings
from .models import User, JobSeekerProfile, Skill, JobSeekerSkill, Education, Experience, OTPVerification
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
    if purpose == 'registration':
        subject = "🔐 Your JobCrest Email Verification OTP"
        body = f"""Hello,

Thank you for registering on JobCrest!

Your One-Time Password (OTP) for email verification is:

    ➤  {otp_code}

This OTP is valid for 10 minutes. Do not share it with anyone.

If you did not register on JobCrest, please ignore this email.

— The JobCrest Team
"""
    else:
        subject = "🔑 Your JobCrest Password Reset OTP"
        body = f"""Hello,

We received a request to reset your JobCrest account password.

Your One-Time Password (OTP) is:

    ➤  {otp_code}

This OTP is valid for 10 minutes. If you did not request a password reset, please ignore this email.

— The JobCrest Team
"""
    send_mail(
        subject=subject,
        message=body,
        from_email=django_settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


# ─────────────────────────────────────────────────────────
# STEP 1 — SEND REGISTRATION OTP
# ─────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
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
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    user.is_verified = True
    user.save()

    otp_obj.is_used = True
    otp_obj.save()

    refresh = RefreshToken.for_user(user)
    return Response({
        "user": UserSerilizer(user).data,
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'detail': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

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
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response({"detail": "Invalid or expired token"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
# JOB SEEKER PROFILE
# ─────────────────────────────────────────────────────────

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated, isJobSeeker])
def jobseeker_profile_view(request):
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    if request.method == 'GET':
        return Response(JobSeekerProfileSerializer(profile).data)
    partial = request.method == 'PATCH'
    serializer = JobSeekerProfileSerializer(profile, data=request.data, partial=partial)
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
        return Response({'detail': 'No resume file provided'}, status=status.HTTP_400_BAD_REQUEST)
    profile.resume = resume_file
    profile.save()
    return Response(JobSeekerProfileSerializer(profile).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def public_jobseeker_profile_view(request, id):
    profile = get_object_or_404(JobSeekerProfile, id=id)
    return Response(JobSeekerProfileSerializer(profile).data)


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
    education = get_object_or_404(Education, pk=pk, jobseeker__user=request.user)
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
    experience = get_object_or_404(Experience, pk=pk, jobseeker__user=request.user)
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
    skill = get_object_or_404(JobSeekerSkill, pk=pk, jobseeker__user=request.user)
    skill.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def all_skills_list_view(request):
    return Response(SkillSerializer(Skill.objects.all(), many=True).data)
