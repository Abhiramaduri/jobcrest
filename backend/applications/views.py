import uuid
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from .models import Application, ApplicationStatusHistory, Interview
from .serializers import (
    ApplicationListSerializer, ApplicationStatusHistorySerializer, ApplicationDetailSerializer,
    ApplicationCreaterSerializer, ApplicationStatusUpdateSerializer, InterviewSerializer,
    ApplicationListSeralizer, ApplicationDetailSeralizer
)
from jobs.models import Job
from accounts.models import JobSeekerProfile
from accounts.permissions import isJobSeeker, IsEmployer, IsJobSeeker
from accounts.lookup import get_object_by_uuid_or_id
from companies.models import EmployerProfile

#---------------------------- Apply to a job ----------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated, isJobSeeker])
def apply_to_job_view(request):
    serializer = ApplicationCreaterSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)

    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    try:
        with transaction.atomic():
            application = serializer.save(applicant=profile)
    except IntegrityError:
        return Response(
            {'detail': 'You have already applied to this job.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    ApplicationStatusHistory.objects.create(
        application=application,
        old_status='',
        new_status='applied',
        changed_by=request.user,
        notes='Application submitted.'
    )
    return Response(ApplicationDetailSerializer(application, context={'request': request}).data, status=status.HTTP_201_CREATED)

#------------------------- Jobseeker's own applications -----------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsJobSeeker])
def my_application_view(request):
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    applications = Application.objects.filter(applicant=profile).order_by('-applied_at')
    return Response(ApplicationListSerializer(applications, many=True).data)

#----------------------------- Application detail / withdraw -------------------------

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def application_detail_view(request, pk):
    application = get_object_by_uuid_or_id(Application, pk)
    
    is_applicant = hasattr(request.user, 'jobseeker_profile') and application.applicant == request.user.jobseeker_profile
    is_employer_owner = hasattr(request.user, 'employer_profile') and application.job.posted_by.user == request.user 
    
    if not (is_applicant or is_employer_owner):
        return Response({
            "detail": "You do not have permission to view this application."
        }, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        return Response(ApplicationDetailSerializer(application, context={'request': request}).data)
    
    if not is_applicant:
        return Response({
            "detail": "Only the applicant can withdraw this application."
        }, status=status.HTTP_403_FORBIDDEN)
    
    with transaction.atomic():
        locked_app = Application.objects.select_for_update().get(pk=application.pk)
        if locked_app.status not in Application.WITHDRAWABLE_STATUSES:
            return Response(
                {"detail": f"Cannot withdraw an application with status '{locked_app.status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        old_status = locked_app.status
        locked_app.status = 'withdrawn'
        locked_app.save(update_fields=['status', 'updated_at'])
        ApplicationStatusHistory.objects.create(
            application=locked_app,
            old_status=old_status,
            new_status='withdrawn',
            changed_by=request.user,
            notes='Application withdrawn by applicant.'
        )

    return Response(
        ApplicationDetailSerializer(locked_app, context={'request': request}).data,
        status=status.HTTP_200_OK
    )

#----------------------------- Update application status ---------------------------

@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsEmployer])
def application_status_update_view(request, pk):
    application = get_object_by_uuid_or_id(Application, pk)
    
    if application.job.posted_by.user != request.user:
        return Response({
            "detail": "You do not have permission to update this application."
        }, status=status.HTTP_403_FORBIDDEN)
    
    with transaction.atomic():
        locked_app = Application.objects.select_for_update().get(pk=application.pk)
        serializer = ApplicationStatusUpdateSerializer(instance=locked_app, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_status = locked_app.status
        new_status = serializer.validated_data['status']
        notes = serializer.validated_data.get('notes', '')
        
        locked_app.status = new_status
        locked_app.save(update_fields=['status', 'updated_at'])
        
        ApplicationStatusHistory.objects.create(
            application=locked_app,
            old_status=old_status,
            new_status=new_status,
            changed_by=request.user,
            notes=notes
        )
    return Response(ApplicationDetailSerializer(locked_app, context={'request': request}).data)

#-------------------------- Status History -----------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def application_history_view(request, pk):
    application = get_object_by_uuid_or_id(Application, pk)
    is_applicant = hasattr(request.user, 'jobseeker_profile') and application.applicant == request.user.jobseeker_profile
    is_employer_owner = hasattr(request.user, 'employer_profile') and application.job.posted_by.user == request.user 
    
    if not (is_applicant or is_employer_owner):
        return Response({
            "detail": "You do not have permission to view this history."
        }, status=status.HTTP_403_FORBIDDEN)
    
    history = application.history.all().order_by('-changed_at')
    return Response(ApplicationStatusHistorySerializer(history, many=True).data)

#------------------- All applications for a specific job ------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployer])
def applications_by_job_view(request, job_id):
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    job = None
    job_id_str = str(job_id).strip()
    try:
        val_uuid = uuid.UUID(job_id_str)
        job = Job.objects.filter(uuid=val_uuid).first()
    except (ValueError, AttributeError):
        pass
    if not job and job_id_str.isdigit():
        job = Job.objects.filter(id=int(job_id_str)).first()
    if not job:
        job = Job.objects.filter(slug=job_id_str).first()

    if not job:
        return Response([], status=status.HTTP_200_OK)

    applications = Application.objects.filter(
        job=job, job__posted_by=employer_profile
    ).order_by('-applied_at')
    return Response(ApplicationListSerializer(applications, many=True).data)

#----------------------- Interviews ---------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployer])
def interview_create_view(request):
    application_id = request.data.get('application')
    application = get_object_by_uuid_or_id(Application, application_id)
    
    if application.job.posted_by.user != request.user:
        return Response({
            "detail": "You do not have permission to schedule this interview."
        }, status=status.HTTP_403_FORBIDDEN)
        
    with transaction.atomic():
        locked_app = Application.objects.select_for_update().get(pk=application.pk)
        old_status = locked_app.status
        allowed = Application.ALLOWED_STATUS_TRANSITIONS.get(old_status, ())
        if old_status != 'interview_scheduled' and 'interview_scheduled' not in allowed:
            return Response(
                {"detail": f"Cannot schedule an interview for an application with status '{old_status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = InterviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        interview = serializer.save()

        if old_status != 'interview_scheduled':
            locked_app.status = 'interview_scheduled'
            locked_app.save(update_fields=['status', 'updated_at'])
        ApplicationStatusHistory.objects.create(
            application=locked_app,
            old_status=old_status,
            new_status='interview_scheduled',
            changed_by=request.user,
            notes='Interview Scheduled.'
        )
    
    return Response(InterviewSerializer(interview).data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def interview_detail_view(request, pk):
    interview = get_object_by_uuid_or_id(Interview, pk)
    application = interview.application
    
    is_applicant = hasattr(request.user, 'jobseeker_profile') and application.applicant == request.user.jobseeker_profile
    is_employer_owner = hasattr(request.user, 'employer_profile') and application.job.posted_by.user == request.user 
    
    if not (is_applicant or is_employer_owner):
        return Response({
            "detail": "You do not have permission to view this interview."
        }, status=status.HTTP_403_FORBIDDEN)
        
    if request.method == 'GET':
        return Response(InterviewSerializer(interview).data)
    
    if not is_employer_owner:
        return Response({
            "detail": "Only the employer can update this interview."
        }, status=status.HTTP_403_FORBIDDEN)
        
    partial = request.method == 'PATCH'
    serializer = InterviewSerializer(interview, data=request.data, partial=partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsJobSeeker])
def my_interviews_view(request):
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    interviews = Interview.objects.filter(application__applicant=profile).order_by('scheduled_at')
    return Response(InterviewSerializer(interviews, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployer])
def employer_interviews_view(request):
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    interviews = Interview.objects.filter(application__job__posted_by=employer_profile).order_by('scheduled_at')
    return Response(InterviewSerializer(interviews, many=True).data)