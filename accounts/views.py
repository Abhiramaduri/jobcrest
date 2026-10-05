from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from .models import User,JobSeekerProfile,Skill,JobSeekerSkill,Education,Experience
from rest_framework import status
# Create your views here.

from .serializers import (
    RegisterSerializer,UserSerilizer,JobSeekerProfileSerializer,SkillSerializer,JobSeekerSkillSerializer,EducationSerializer,ExperienceSerializer
)
from .permissions import isJobSeeker

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer=RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user=serializer.save()
    refresh=RefreshToken.for_user(user)
    return Response({
        "user":UserSerilizer(user).data,
        "refresh":str(refresh),
        "access":str(refresh.access_token)
        },status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username=request.data.get('username')
    password=request.data.get('password')

    if not username or not password:
        return Response({
            "detail":"Username and password are required"
        },status=status.HTTP_400_BAD_REQUEST)
    user=authenticate(username=username,password=password)
    if user is None:
        return Response({
            "detail":"invalid credentials"
        },status=status.HTTP_401_UNAUTHORIZED)
    refresh=RefreshToken.for_user(user)
    return Response({
        "user":UserSerilizer(user).data,
        "refresh":str(refresh),
        "access":str(refresh.access_token)
        })
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token=request.data["refresh"]
        token=RefreshToken(refresh_token)
        token.blacklist()
        return Response({
            "detail":"Logged out successfully"
        },status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response({"detail":"Invalid or reset token"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(UserSerilizer(request.user).data)

@api_view(['POST'])
@permission_classes({AllowAny})
def password_reset_request_view(request):
    email=request.data.get("email")
    if not email:
        return Response({
            "detail":"Email is required"
        })
    return Response({
        "detail":"If that email exists, a reset link has been sent."
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request_view(request):
    new_password=request.data.get("new_password")
    try:
        validate_password(new_password)
    except DjangoValidationError as e:
        return Response({"password":e.message},status=status.HTTP_400_BAD_REQUEST)
    return Response({"detail":"Password has been reset"})



#----------------------------- JobSeeker Profile ----------------------------------------

@api_view(['GET','PUT','PATCH'])
@permission_classes([IsAuthenticated,isJobSeeker])
def jobseeker_profile_view(request):
    profile=get_object_or_404(JobSeekerProfile,user=request.user)

    if request.method=='GET':
        return Response(JobSeekerProfileSerializer(profile).data)
    partial=request.method=='PATCH'
    serilizer=JobSeekerProfileSerializer(profile,data=request.data,partial=partial)
    serilizer.is_valid(raise_exception=True)
    serilizer.save()
    return Response(serilizer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated,isJobSeeker])
@parser_classes([MultiPartParser,FormParser])
def jobseeker_resume_upload_view(request):
    profile=get_object_or_404(JobSeekerProfile,user=request.user)
    resume_file=request.Files.get('resume')
    if not resume_file:
        return Response({
            "detail":"No Resume file provided"
        },status=status.HTTP_400_BAD_REQUEST)
    profile.resume=resume_file
    profile.save()
    return Response(JobSeekerProfileSerializer(profile).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def public_jobseeker_profile_view(request,id):
    profile=get_object_or_404(JobSeekerProfile,id=id)
    return Response(JobSeekerProfileSerializer(profile).data)    


#----------------------------Education------------------------------------------

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated,isJobSeeker])
def education_list_create_view(request):
    profile=get_object_or_404(JobSeekerProfile,user=request.user)

    if request.method=='GET':
        education=Education.objects.filter(jobseeker=profile)
        return Response(EducationSerializer(education,many=True).data)
    serializer=EducationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(jobseeker=profile)
    return Response(serializer.data,status=status.HTTP_201_CREATED)



@api_view(['GET','PUT','PATCH','DELETE'])
@permission_classes([IsAuthenticated,isJobSeeker])
def education_detail_view(request,pk):
    education = get_object_or_404(Education, pk=pk, jobseeker__user = request.user)
    if request.method=='GET':
        return Response(EducationSerializer(education).data)

    if request.method=='DELETE':
        education.delete()
        return Response({
            "message": "Education Deleted"
        }, status = status.HTTP_204_NO_CONTENT)

    partial=request.method=='PATCH'
    serializer = EducationSerializer(education, data = request.data, partial=partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)