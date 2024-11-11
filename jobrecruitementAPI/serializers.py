from rest_framework import serializers  # Importing the serializers module from Django REST Framework
from .models import PlatformUser, Skill, Education, Experience, Project  # Importing the relevant models
import uuid  # Importing the uuid library for unique ID generation
from rest_framework_simplejwt.tokens import RefreshToken  # Importing RefreshToken for token management
import random  # Importing random for generating random numbers
from datetime import datetime  # Importing datetime for handling date and time

class FlexibleDateField(serializers.DateField):
    def to_internal_value(self, data):
        # Try multiple date formats
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(data, fmt).date()
            except ValueError:
                continue
        # Fall back to the default validation
        return super().to_internal_value(data)
    
# Serializer for blacklisting refresh tokens
class BlacklistTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()  # Field for the refresh token

    def validate(self, attrs):
        self.token = attrs['refresh_token']  # Storing the refresh token for later use
        return attrs  # Returning the validated attributes

    def save(self, **kwargs):
        try:
            # Use the refresh token to blacklist it
            token = RefreshToken(self.token)  # Create a RefreshToken instance
            token.blacklist()  # Blacklist the token
        except Exception as e:
            self.fail('bad_token')  # Raise an error if blacklisting fails

# Serializer for the Skill model
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill  # Specifying the model to be serialized
        fields = ['name']  # Fields to include in the serialized output

    def create(self, validated_data):
        # Create skills and associate them with the user
        print("here skills", validated_data)  # Debug print statement
        return Skill.objects.create(user= self.user,**validated_data)  # Create and return a Skill instance

# Serializer for the Education modelclass 
class EducationSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    class Meta:
        model = Education
        fields = [
            'institution', 'field', 'education_level', 'board', 
            'passing_out_year', 'school_medium', 'grading_system', 'total_marks', 
            'course_type', 'specialization', 'start_date', 'end_date', 'still_studying' 
        ]


class ProjectSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(queryset=PlatformUser.objects.all())  # Link to PlatformUser

    class Meta:
        model = Project
        fields = ['project_title', 'project_summary', 'project_link']

# Serializer for the Experience model
class ExperienceSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(queryset=PlatformUser.objects.all())  # Link to PlatformUser

    class Meta:
        model = Experience
        fields = [
            'job_title', 'company', 'location', 'start_date', 'end_date',
            'employment_type', 'responsibilities', 'job_summary', 'primary_skills',
            'tools_technologies', 'domain_knowledge', 'annual_salary', 'fixed_salary',
            'variable_salary', 'currently_working'
        ]

    def create(self, validated_data):
        # Create experience and associate it with the user
        return Experience.objects.create(**validated_data)  

# Serializer for the PlatformUser model
class PlatformUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    unique_id = serializers.CharField(read_only=True)
    skills = SkillSerializer(many=True, required=False)
    educations = EducationSerializer(many=True, required=False)
    experiences = ExperienceSerializer(many=True, required=False)
    
    govt_employee = serializers.BooleanField(required=False)
    ex_military = serializers.BooleanField(required=False)
    reserve_forces = serializers.BooleanField(required=False)
    military = serializers.BooleanField(required=False)

    class Meta:
        model = PlatformUser
        fields = [
            'id', 'username', 'unique_id', 'email', 'password', 'name', 'country', 
            'city', 'phone', 'current_address', 'permanent_address', 'state', 
            'pin_code', 'gender', 'birth_date', 'role', 'adhaar_number',
            'disability_status', 'govt_employee', 'ex_military', 'reserve_forces', 
            'military', 'current_ctc', 'expected_ctc', 'skills', 'educations', 'experiences'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        educations_data = validated_data.pop('educations', [])
        skills_data = validated_data.pop('skills', [])
        experiences_data = validated_data.pop('experiences', [])
        
        user = PlatformUser(**validated_data)
        user.set_password(password)
        user.save()

        for education in educations_data:
            Education.objects.create(user=user, **education)

        for skill in skills_data:
            Skill.objects.create(user=user, **skill)

        for experience in experiences_data:
            Experience.objects.create(user=user, **experience)

        return user