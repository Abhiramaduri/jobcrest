from rest_framework import serializers
from .models import Application, ApplicationStatusHistory,Interview
from jobs.serializers import JobListSerializer

class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_username=serializers.CharField(source='changed_by.username',read_only=True)

    class Meta:
        model=ApplicationStatusHistory
        fields=('Id','old_status','new_status','changed_by','changed_by_username','changed_at','notes')
        read_only_fields=('id','changed_by','changed_at')

class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model:Interview
        fields=(
            'id','application','schedule_at','mode','meeting_link','interviewer_notes','feedback','result'
        )
        read_only_fields=('id',)

class ApplicationListSeralizer(serializers.ModelSerializer):
    job_title=serializers.CharField(source='job_title',read_only=True)
    company_name=serializers.CharField(source='job.company.name',read_only=True)
    applicant_name=serializers.CharField(source='applicant,full_name',read_only=True)

    class Meta:
        model=Application
        fields=(
            'id','job','job_title','company_name','applicant','application_name','status','applied_at',
        )

        class Meta:
            model=Application
            fields=(
                'id','job_title','company_name','applicant','applicant_name','status_name','status','applied_at',
            )
class ApplicationDetailSerializer(serializers.ModelSerializer):
    job=JobListSerializer(read_only=True)
    applicant_name=serializers.CharField(source='application.full_name',read_only=True)
    history = ApplicationStatusHistorySerializer(many=True, read_only=True)
    interviews= InterviewSerializer(many=True, read_only=True)

    class Meta:
        model= Application
        fields=(
            'id','job','applicant','applicant_name','resume','cover_letter'
        )
        read_only_fields=('id','applicant','applied-at','updated_at')

class ApplicationCreaterSerializer(serializers.ModelSerializer):
    class Meta:
        model=Application
        fields=('id','job','resume','cover_letter')
        read_only_fields=('id',)

    def validate(self,attrs):
        request=self.context['request']
        job=attrs['job']
        profile=request.user.jobseeker_profile
        if Application.objects.filter(job=job,applicant=profile).exists():
            raise serializers.ValidationError("You have already applied to this job")
        return attrs

class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    notes=serializers.CharField(write_only=True,required=False,allow_blank=True)

    class Meta:
        model= Application
        fields=('status','notes')