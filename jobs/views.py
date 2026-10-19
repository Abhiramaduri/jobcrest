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
    skills = Skill.objects.all()
    return Response(SkillSerializer(skills, many=True).data)

#--------------------------------------- Job List / Create -------------------------------------------------------------

@api_view(['GET','POST'])
@permission_classes([AllowAny])
def job_list_create_view(request):
    if request.method=='GET':
        queryset=Job.objects.filter(status='published').select_related('company','category')
        job_filter=JobFilter(request.GET,queryset=queryset)
        queryset=job_filter.qs
        search_term=request.GET.get('search')

        if search_term:
            queryset=queryset.filter(Q(title__icontains=search_term)|Q(description__icontains=search_term))
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

@api_view(['GET','PUT','PATCH','DELETE'])
@permission_classes([AllowAny])
def job_detail_view(request,slug):
    job=get_object_or_404(Job,slug=slug)

    if request.method=='GET':
        job.views_count +=1
        job.save(update_fields=['views_count'])
        return Response(JobDetailSerializer(job).data)
    if not request.user.is_authenticated:
        return Response({
            "detail":"Authentication required."
        },status=status.HTTP_401_UNAUTHORIZED)
    if not job.posted_by or job.posted_by.user != request.user:
        return Response({
            "detail":"You do not have permission to modify this job."
        },status=status.HTTP_403_FORBIDDEN)
    if request.method=='DELETE':
        job.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    partial = request.method =='PATCH'
    serializer=JobWriterSerializer(job,data=request.data,partial=partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(JobDetailSerializer(job).data)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated,IsEmployer])
def job_status_update_view(request,slug):
    job=get_object_or_404(Job,slug=slug)

    if job.posted_by.user != request.user:
        return Response({
            "detail":"You do not have permission to modify this job."
        },status=status.HTTP_403_FORBIDDEN)

    new_status=request.data.get('status')
    valid_statuses=[choice[0] for choice in Job.STATUS_CHOICE]

    if new_status not in valid_statuses:
        return Response({
            "detail":f"Status must be one of {valid_statuses}."
        },status=status.HTTP_400_BAD_REQUEST)
    job.status=new_status
    job.save(update_fields=['status'])
    return Response(JobDetailSerializer(job).data)

#-------------------------Applicants for a Job -------------------------------------------------------

# @api_view(['GET'])
# @permission_classes([IsAuthenticated,IsEmployer])
# def job_applicants_view(request,slug):
#     job=get_object_or_404(Job,slug=slug)

#     if job.posted_by.user !=request.user:
#         return Response({
#             "detail":"You do not have permissions to view these applicants."
#         },status=status.HTTP_403_FORBIDDEN)

#     from applications.serilizers import ApplicationListSerializer
#     applications = job.application.all().order_by('-applied_at')
#     return Response(ApplicationListSerializer(applications,many=True).data)

#-------------------------- Employer's own postings ------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated,IsEmployer])
def my_postings_view(request):
    employers_profile=get_object_or_404(EmployerProfile,user=request.user)
    jobs=Job.objects.filter(posted_by=employers_profile).order_by('-created_at')
    return Response(JobListSerializer(jobs,many=True).data)

#-------------------Recommended jobs for a jobseeker -----------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated,isJobSeeker])
def recommended_jobs_view(request):
    profile=get_object_or_404(JobSeekerProfile,user=request.user)
    skills_ids=list(profile.skills.values_list('skill_id',flat=True)[:5])

    if not skills_ids:
        return Response([])
    jobs=Job.objects.filter(
        status='published',skill_required__in=skills_ids
    ).distinct().order_by('-created_at')

    return Response(JobListSerializer(jobs,many=True).data)

#---------------------------- Saved Jobs --------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated,isJobSeeker])
def saved_jobs_list_view(request):
    profile=get_object_or_404(JobSeekerProfile,user=request.user)
    saved=SavedJob.objects.filter(jobseeker=profile).order_by('-saved_at')
    return Response(SavedJobSerializer(saved,many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated,isJobSeeker])
def save_job_view(request,slug):
    job=get_object_or_404(Job,slug=slug)
    profile=get_object_or_404(JobSeekerProfile,user=request.user)

    saved,created=SavedJob.objects.get_or_create(jobseeker=profile,job=job)
    if not created:
        return Response({
            "detail":"Job already saved"
        },status=status.HTTP_400_BAD_REQUEST)
    return Response(SavedJobSerializer(saved).data,status=status.HTTP_201_CREATED)

sav_job_view = save_job_view

@api_view(['DELETE'])
@permission_classes([IsAuthenticated,isJobSeeker])
def unsave_job_view(request,slug):
    job=get_object_or_404(Job,slug=slug)
    profile=get_object_or_404(JobSeekerProfile,user=request.user)

    saved_job=get_object_or_404(SavedJob,jobseeker=profile,job=job)
    saved_job.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)