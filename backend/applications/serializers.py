from rest_framework import serializers
from .models import Application, ApplicationStatusHistory, Interview
from jobs.serializers import JobListSerializer

class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = ApplicationStatusHistory
        fields = ('id', 'old_status', 'new_status', 'changed_by', 'changed_by_username', 'changed_at', 'notes')
        read_only_fields = ('id', 'changed_by', 'changed_at')

class InterviewSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='application.job.title', read_only=True)
    company_name = serializers.CharField(source='application.job.company.name', read_only=True)
    applicant_name = serializers.CharField(source='application.applicant.full_name', read_only=True)
    meeting_link = serializers.CharField(max_length=500, required=False, allow_blank=True, default='')
    interview_notes = serializers.CharField(required=False, allow_blank=True, default='')
    result = serializers.CharField(max_length=20, required=False, default='pending')

    class Meta:
        model = Interview
        fields = (
            'id', 'application', 'scheduled_at', 'mode', 'meeting_link', 'interview_notes', 'result',
            'job_title', 'company_name', 'applicant_name'
        )
        read_only_fields = ('id', 'job_title', 'company_name', 'applicant_name')

    def validate_mode(self, value):
        val = str(value).lower().strip()
        if val in ('virtual', 'online'):
            return 'virtual'
        elif val in ('in-person', 'in_person'):
            return 'in_person'
        elif val == 'phone':
            return 'phone'
        return val

class ApplicationListSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company.name', read_only=True)
    applicant_name = serializers.CharField(source='applicant.full_name', read_only=True)

    class Meta:
        model = Application
        fields = (
            'id', 'job', 'job_title', 'company_name', 'applicant', 'applicant_name', 'status', 'applied_at'
        )

ApplicationListSeralizer = ApplicationListSerializer

class ApplicationDetailSerializer(serializers.ModelSerializer):
    job = JobListSerializer(read_only=True)
    applicant_name = serializers.CharField(source='applicant.full_name', read_only=True)
    history = ApplicationStatusHistorySerializer(many=True, read_only=True)
    interviews = InterviewSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = (
            'id', 'job', 'applicant', 'applicant_name', 'resume', 'cover_letter',
            'status', 'history', 'interviews', 'applied_at', 'updated_at'
        )
        read_only_fields = ('id', 'applicant', 'applied_at', 'updated_at')

ApplicationDetailSeralizer = ApplicationDetailSerializer

class ApplicationCreaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ('id', 'job', 'resume', 'cover_letter')
        read_only_fields = ('id',)

    def validate(self, attrs):
        request = self.context['request']
        job = attrs['job']
        profile = getattr(request.user, 'jobseeker_profile', None)
        if profile and Application.objects.filter(job=job, applicant=profile).exists():
            raise serializers.ValidationError("You have already applied to this job")
        return attrs

ApplicationCreateSerializer = ApplicationCreaterSerializer

class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    notes = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Application
        fields = ('status', 'notes')