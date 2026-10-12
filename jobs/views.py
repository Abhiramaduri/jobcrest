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

#--------------------------------------- Job List / Create -------------------------------------------------------------

@api_view('GET','POST')
@permission_classes([AllowAny])
def job_list_create_view(request):
    if request.method=='GET':
        queryset=Job.objects.filter(status='published').select_related('company','category')
        Job.objects.filter(status='published').select_related('company','category')
        job_filter=JobFilter(request.GET,queryset=queryset)
        queryset=job_filter.qs
        search_term=request.GET.get('search')

        if search_term:
            queryset=queryset.filter(Q(title_icontains=search_term)|Q(description_icontains=search_term))
        ordering=request.GET.get('ordering','-created_at')
        queryset=queryset.order_by(ordering)

        return Response(JobListSerializer(queryset,many=True).data)
    
    if not request.user.is_authenticated:
        return Response({
            "detail": "Authentication required."
        }, status=status.HTTP_401_UNAUTHORIZED)
        
    if request.user.user_type != 'employer':
        return Response({
            "detail": "Only can post Job."
        }, status=status.HTTP_403_FORBIDDEN)
    
    employer_profile=get_object_or_404(EmployerProfile,user=request.user)
    serializer=JobWriterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    job=serializer.save(posted_by=employer_profile,company=employer_profile.company)

    return Response(JobDetailSerializer(job).data,status=status.HTTP_201_CREATED)
        