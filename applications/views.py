from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Application,ApplicationStatusHistory,Interview
from .serializers import(
    ApplicationListSeralizer,ApplicationStatusHistorySerializer,ApplicationDetailSerializer,ApplicationCreaterSerializer,ApplicationStatusUpdateSerializer,InterviewSerializer
)
from accounts.models import JobSeekerProfile
from accounts.permissions import isJobSeeker,IsEmployer
from companies.models import EmployerProfile

#---------------------------- Apply to a job ----------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated,isJobSeeker])
def apply_to_job_view(request):
    serializer=ApplicationCreaterSerializer(data=request.data,context={'request':request})
    serializer.is_valid(raise_exception=True)

    profile=get_object_or_404(JobSeekerProfile,user=request.user)
    application=serializer.save(applicant=profile)
    ApplicationStatusHistory.objects.create(
        application=application,
        old_status='',
        new_status='applied',
        changed_by=request.user,
        notes='Application submitted.'
    )
    return Response(ApplicationDetailSerializer(application).data,status=status.HTTP_201_CREATED)