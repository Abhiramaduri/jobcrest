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
