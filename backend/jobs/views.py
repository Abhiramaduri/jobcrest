from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.settings import api_settings
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.db.models import F, Q
from .models import JobCategory,JobCategory,Job,SavedJob
from .filters import JobFilter
from .serializers import(
    JobCategorySerializer,JobListSerializer,JobDetailSerializer,JobWriterSerializer,SavedJobSerializer
)
from accounts.models import Skill,JobSeekerProfile
from accounts.permissions import IsEmployer,isJobSeeker
from accounts.throttles import get_client_ip
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

class _JobOrderingConfig:
    """Strict whitelist for job listing ordering via DRF OrderingFilter."""
    ordering_fields = ('created_at', 'salary_min', 'salary_max', 'title', 'views_count')
    ordering = ('-created_at',)


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

        queryset = OrderingFilter().filter_queryset(request, queryset, _JobOrderingConfig)

        paginator_class = api_settings.DEFAULT_PAGINATION_CLASS
        if paginator_class is not None:
            paginator = paginator_class()
            page = paginator.paginate_queryset(queryset, request)
            if page is not None:
                serializer = JobListSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

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

BOT_USER_AGENT_KEYWORDS = (
    'bot', 'crawler', 'spider', 'slurp', 'scrapy', 'headlesschrome',
    'phantomjs', 'lighthouse', 'curl/', 'wget/', 'python-requests',
    'go-http-client', 'httpclient',
)
VIEW_DEDUPE_TTL_SECONDS = 3600


def _should_count_job_view(request, job):
    """Skip automated bots/crawlers and deduplicate repeated refreshes per user or IP."""
    user_agent = (request.META.get('HTTP_USER_AGENT') or '').lower()
    if user_agent and any(keyword in user_agent for keyword in BOT_USER_AGENT_KEYWORDS):
        return False

    if getattr(request, 'user', None) and request.user.is_authenticated:
        viewer_ident = f"user:{request.user.pk}"
    else:
        viewer_ident = f"ip:{get_client_ip(request)}"

    dedupe_key = f"job_view:{job.pk}:{viewer_ident}"
    return cache.add(dedupe_key, True, timeout=VIEW_DEDUPE_TTL_SECONDS)


@api_view(['GET','PUT','PATCH','DELETE'])
@permission_classes([AllowAny])
def job_detail_view(request,slug):
    job=get_object_or_404(Job,slug=slug)

    if request.method=='GET':
        if _should_count_job_view(request, job):
            Job.objects.filter(pk=job.pk).update(views_count=F('views_count') + 1)
            job.refresh_from_db(fields=['views_count'])
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
        if job.status == 'closed':
            return Response(
                {"detail": "Job posting is already closed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        job.status = 'closed'
        job.save(update_fields=['status', 'updated_at'])
        return Response(JobDetailSerializer(job).data, status=status.HTTP_200_OK)

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

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated,isJobSeeker])
def unsave_job_view(request,slug):
    job=get_object_or_404(Job,slug=slug)
    profile=get_object_or_404(JobSeekerProfile,user=request.user)

    saved_job=get_object_or_404(SavedJob,jobseeker=profile,job=job)
    saved_job.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)