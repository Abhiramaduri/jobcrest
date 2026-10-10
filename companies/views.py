from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from .models import Company, EmployerProfile
from .serializers import CompanySerializer, CompanyListSerializer, EmployerProfileSerializer
from accounts.permissions import IsEmployer


@api_view(['GET','POST'])
@permission_classes([AllowAny])
def company_list_create_view(request):
    if request.method == 'GET':
        companies = Company.objects.all().order_by('-created_at')
        return Response(CompanyListSerializer(companies, many=True).data)
    
    if not request.user.is_authenticated:
        return Response({
            "detail": "Authentication Required."
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if request.user.user_type != 'employer':
        return Response({
            "detail": "Only employers can create a company. "
        }, status=status.HTTP_403_FORBIDDEN)

    serializer=CompanyListSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    company=serializer.save(created_by=request.user)

    EmployerProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'company':company,
            'designation':'Admin',
            'is_company_admin': True
        }
    )
    return Response(CompanySerializer(company).data, status=status.HTTP_201_CREATED)


@api_view(['GET','PUT','PATCH','DELETE'])
@permission_classes([AllowAny])
def company_detail_view(request,slug):
    company=get_object_or_404(CompanySerializer(company).data)

    if request.method=='GET':
        return Response(CompanySerializer(company).data)
    if not request.user.is_authenticated:
        return Response({
            "detail":"Authentication required."
        },status=status.HTTP_401_UNAUTHORIZED)

    if company.created_by != request.user:
        return Response({
            "detail":"You do not have permission to modify this company."
        },status=status.HTTP_403_FORBIDDEN)
    if request.method=='DELETE':
        company.delete()
        return Response(status.HTTP_204_NO_CONTENT)
    partial=request.method=='PATCH'
    serializer=CompanySerializer(company,data=request.data,partial=partial)
    serializer.save()
    return Response(serializer.data)

# @api_view(['GET'])
# @permission_classes([AllowAny])
# def company_jobs_view(request,slug):
#     company=get_object_or_404(Company,slug=slug)

#     from jobs.serializers import JobListSerializer
#     jobs=company.jobs.filter(status='published').order_by('-created_at')
#     return Response(JobListSerializer(jobs,many=True).data)




#------------------------------ Recruiters (EmployerProfile) ----------------------


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated,IsEmployer])
def company_recruiters_view(request,slug):
    company=get_object_or_404(Company,slug=slug)

    if request.method=='GET':
        recruiters=EmployerProfile.object.filter(company=company)
        return Response(EmployerProfileSerializer(recruiters,many=True).data)
    requester_profile=get_object_or_404(EmployerProfile,user=request,company=company)
    if not requester_profile.is_company_admin:
        return Response({
            "detail":"Only a company admin can add recruiters."
        },status=status.HTTP_403_FORBIDDEN)
    serializer = EmployerProfileSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(company=company)
    return Response(serializer.data,status=status.HTTP_201_CREATED)


#------------------------------------Employers own Profile -----------------------------------------

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsEmployer])
def employer_profile_view(request):
    profile = get_object_or_404(EmployerProfile, user=request.user)
    
    if request.method == 'GET':
        return Response(EmployerProfileSerializer(profile).data)
    
    partial = request.method == 'PATCH'
    serializer = EmployerProfileSerializer(profile, data= request.data, partial = partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)