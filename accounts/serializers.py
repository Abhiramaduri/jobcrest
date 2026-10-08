from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, JobSeekerProfile,Skill,JobSeekerSkill,Education,Experience

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, validators = [validate_password])
    password2=serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields=('username','email','password','password2','user_type','phone_number')

    def validate(self,attrs):
        if attrs['password'] != attrs['password2'] :
            raise serializers.ValidationError
        return attrs
    def create(self, validated_data):
        self.validated_data.pop('password2')
        user =  User.objects.create_user(
        username=validated_data['username'],
        email=validated_data['email'],
        password=validated_data['password'],
        user_type = validated_data['user_type'],
        phone_number = validated_data['phone_number']
        )
        if user.user_type=='jobseeker':
            JobSeekerProfile.objects.create(user=user,full_name=user.username)
            return user
class UserSerilizer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('id','username','email','user_type','phone_number','is_verified','created_at')
        read_only_fields=('id','is_verified','created_at')

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('id', 'name')

class JobSeekerSkillSerializer(serializers.ModelSerializer):
    skill_name=serializers.CharField(source='skill.name',read_only=True)

    class Meta:
        model=JobSeekerSkill
        fields=('id','skill','skill_name','proficiency')

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Education
        fields=('id','degree','institution','field_of_study','start_year','end_year','grade')

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model=Experience
        fields=('id','company_name','role_title','start_date','end_date','is_current','description')

class JobSeekerProfileSerializer(serializers.ModelSerializer):
    skils=JobSeekerSkillSerializer(many=True,read_only=True)
    education=EducationSerializer(many=True,read_only=True)
    experience=ExperienceSerializer(many=True,read_only=True)
    username=serializers.CharField(source='user.username',read_only=True)

    class Meta:
        model=JobSeekerSkill
        fields=(
            'id','username','email','full_name','headline','bio','resume','profile_picture', 'date_of_birth', 'location', 'experience_years', 'current_ctc',
            'expected_ctc', 'linkedin_url', 'github_url', 
            'portfolio_url', 'is_open_to_work', 'skills', 'education', 'experience'
        )
