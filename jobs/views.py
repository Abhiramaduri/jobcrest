from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.filters import SearchFilter,OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import JobCategory,JobCategory,Job,SavedJob
from .filters import JobFilter
from .serializers import(
    JobCategorySerializer,JobListSerializer,JobDetailSerializer,JobWriterSerializer,SavedJobSerializer
)
from accounts.models import Skill,JobSeekerProfile
from accounts.permissions import IsEmployer,isJobSeeker
from companies.models import EmployerProfile
from accounts.serializers import SkillSerializer

#-----------------------------------Categories & Skills(reference data) ------------------------------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def job_category_list_view(request):
    categories=JobCategory.objects.all()
    return Response(JobCategorySerializer(categories,many=True).data)

@api_view(['GET'])
@permission_classes([AllowAny])
def job_skills_list_view(request):
    skills=SkillSerializer.all()
    return Response(SkillSerializer(skills,many=True).data)

