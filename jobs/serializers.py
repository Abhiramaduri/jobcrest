from rest_framework import serializers
from .models import JobCategory, Job, SavedJob
from accounts.models import Skill
from accounts.serializers import SkillSerializer
from companies.serializers import CompanyListSerializer

class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=JobCategory
        fields=('id','name','slug')
        read_only_fields=('slug'),
class JobListSerializer(serializers.ModelSerializer):
    comapany=CompanyListSerializer(read_only=True)
    category_name=CharField(source='category.name',read_only=True)

    class Meta:
        model=Job
        fields=(
            'id','title','slug','company','category_name','job_type',
            'location','is_remote','salary_min','salary_max','salary_currency'
        )

class JobDetailSerializer(serializers.ModelSerializer):
    company=CompanyListSerializer(read_only=True)
    category=JobCategorySerializer(read_only=True)
    skills_required=SkillSerializer(many=True,read_only=True)
    posted_by_username=serializers.CharField(source='posted_by.user.username', read_only=True)

    class Meta:
        model=Job
        fields=(
            'id','title','slug','company','posted_by','posted_by_username', 'category', 'description', 'responsibilities', 'requirements',
            'job_type', 'experience_min', 'experience_max', 'salary_min',
            'salary_max', 'salary_currency', 'location', 'is_remote',
            'skills_required', 'vacancies', 'status', 'application_deadline',
            'created_at', 'updated_at',
        )
        read_only_fields=('id','slug','posted_by','created_at','updated_at','views_count')


class JobWriterSerializer(serializers.ModelSerializer):
    skills_required=serializers.PrimaryKeyRelatedField(
        many=True,queryset=Skill.objects.all(),required=False
    )

    class Meta:
        model=Job
        fields=(
            'id','title','company','category','description','responsibilities',
            'requirements', 'job_type', 'experience_min', 'experience_max', 'salary_min', 'salary_max', 'salary_currency',
            'location', 'is_remote', 'skills_required', 'vacancies', 'status', 'application_deadline',
        )
        read_only_fields=('id',)
class SavedJobSerializer(serializers.ModelSerializer):
    job=JobListSerializer(read_only=True)

    class Meta:
        model=SavedJob
        fields=('id','job','saved_at')
        read_only_fields=('id','saved_at')