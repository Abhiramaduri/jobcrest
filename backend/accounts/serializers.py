from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, JobSeekerProfile, Skill, JobSeekerSkill, Education, Experience
from .resume_security import generate_signed_resume_url

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'user_type', 'phone_number')

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            user_type=validated_data['user_type'],
            phone_number=validated_data.get('phone_number', '')
        )
        if user.user_type == 'jobseeker':
            JobSeekerProfile.objects.create(user=user, full_name=user.username)
        return user

class UserSerilizer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'uuid', 'username', 'email', 'user_type', 'phone_number', 'is_verified', 'created_at')
        read_only_fields = ('id', 'uuid', 'is_verified', 'created_at')

UserSerializer = UserSerilizer

class SkillSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = Skill
        fields = ('id', 'uuid', 'name')
        read_only_fields = ('id', 'uuid')

class JobSeekerSkillSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = JobSeekerSkill
        fields = ('id', 'uuid', 'skill', 'skill_name', 'proficiency')
        read_only_fields = ('id', 'uuid')

class EducationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = Education
        fields = ('id', 'uuid', 'degree', 'institution', 'field_of_study', 'start_year', 'end_year', 'is_current', 'grade')
        read_only_fields = ('id', 'uuid')

class ExperienceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = Experience
        fields = ('id', 'uuid', 'company_name', 'role_title', 'start_date', 'end_date', 'is_current', 'description')
        read_only_fields = ('id', 'uuid')

class JobSeekerProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    skills = JobSeekerSkillSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    experience = ExperienceSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    resume = serializers.SerializerMethodField()

    def get_resume(self, obj):
        if obj.resume:
            request = self.context.get('request') if isinstance(self.context, dict) else None
            return generate_signed_resume_url(obj.resume.name, request=request)
        return None

    class Meta:
        model = JobSeekerProfile
        fields = (
            'id', 'uuid', 'username', 'email', 'full_name', 'headline', 'bio', 'resume', 'profile_picture',
            'date_of_birth', 'location', 'experience_years', 'current_ctc', 'expected_ctc',
            'linkedin_url', 'github_url', 'is_open_to_work', 'skills', 'education', 'experience'
        )
        read_only_fields = ('id', 'uuid', 'username', 'email', 'resume')
