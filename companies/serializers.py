from rest_framework import serializers
from .models import Company,EmployerProfile

class CompanySerializer(serializers.ModelSerializer):
    created_by_username=serializers.CharField(source='created_by.username',read_only=True)

class Meta:
    model=Company
    fields=(
        'id','name','slug','logo','description','website','industry','company_size','founded_year',
        'location','created_by','created_by_username','created_at',
    )
    read_only_fields=('id','slug','created_by','created_at')

class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model=Company
        fields=('id','name','slug','logo','industry','location','company_size')

class EmployerProfileSerializer(serializers.ModelSerializer):
    username=serializers.CharField(source='user.username',read_only=True)
    email=serializers.CharField(source='user.email',read_only=True)
    company_name=serializers.CharField(source='company.name',read_only=True)

    class Meta:
        model=EmployerProfile
        fields=(
            'id','username','email','company','company_name','designation','is_company_admin'
        )
        read_only_fields=('id',)