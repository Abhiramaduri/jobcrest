from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Application, ApplicationStatusHistory, Interview
from .serializers import (
    ApplicationListSerializer, ApplicationStatusHistorySerializer, ApplicationDetailSerializer,
    ApplicationCreaterSerializer, ApplicationStatusUpdateSerializer, InterviewSerializer,
    ApplicationListSeralizer, ApplicationDetailSeralizer
)
from accounts.models import JobSeekerProfile
from accounts.permissions import isJobSeeker, IsEmployer, IsJobSeeker
from companies.models import EmployerProfile

#---------------------------- Apply to a job ----------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated, isJobSeeker])
def apply_to_job_view(request):
    serializer = ApplicationCreaterSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)

    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    application = serializer.save(applicant=profile)
    ApplicationStatusHistory.objects.create(
        application=application,
        old_status='',
        new_status='applied',
        changed_by=request.user,
        notes='Application submitted.'
    )
    return Response(ApplicationDetailSerializer(application).data, status=status.HTTP_201_CREATED)

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
    application = get_object_or_404(Application, pk=pk)
    
    is_applicant = hasattr(request.user, 'jobseeker_profile') and application.applicant == request.user.jobseeker_profile
    is_employer_owner = hasattr(request.user, 'employer_profile') and application.job.posted_by.user == request.user 
    
    if not (is_applicant or is_employer_owner):
        return Response({
            "detail": "You do not have permission to view this application."
        }, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        return Response(ApplicationDetailSerializer(application).data)
    
    if not is_applicant:
        return Response({
            "detail": "Only the applicant can withdraw this application."
        }, status=status.HTTP_403_FORBIDDEN)
    
    application.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

#----------------------------- Update application status ---------------------------

@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsEmployer])
def application_status_update_view(request, pk):
    application = get_object_or_404(Application, pk=pk)
    
    if application.job.posted_by.user != request.user:
        return Response({
            "detail": "You do not have permission to update this application."
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ApplicationStatusUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    old_status = application.status
    new_status = serializer.validated_data['status']
    notes = serializer.validated_data.get('notes', '')
    
    application.status = new_status
    application.save(update_fields=['status', 'updated_at'])
    
    ApplicationStatusHistory.objects.create(
        application=application,
        old_status=old_status,
        new_status=new_status,
        changed_by=request.user,
        notes=notes
    )
    return Response(ApplicationDetailSerializer(application).data)

#-------------------------- Status History -----------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def application_history_view(request, pk):
    application = get_object_or_404(Application, pk=pk)
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
    applications = Application.objects.filter(
        job_id=job_id, job__posted_by=employer_profile
    ).order_by('-applied_at')
    return Response(ApplicationListSerializer(applications, many=True).data)

#----------------------- Interviews ---------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployer])
def interview_create_view(request):
    application_id = request.data.get('application')
    application = get_object_or_404(Application, pk=application_id)
    
    if application.job.posted_by.user != request.user:
        return Response({
            "detail": "You do not have permission to schedule this interview."
        }, status=status.HTTP_403_FORBIDDEN)
        
    serializer = InterviewSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    interview = serializer.save()
    
    application.status = 'interview_scheduled'
    application.save(update_fields=['status', 'updated_at'])
    ApplicationStatusHistory.objects.create(
        application=application,
        old_status=application.status,
        new_status='interview_scheduled',
        changed_by=request.user,
        notes='Interview Scheduled.'
    )
    
    return Response(InterviewSerializer(interview).data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def interview_detail_view(request, pk):
    interview = get_object_or_404(Interview, pk=pk)
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