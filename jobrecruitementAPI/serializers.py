from rest_framework import serializers
from .models import PlatformUser, Skill, Education, Experience, DesiredJob
import uuid
from rest_framework_simplejwt.tokens import RefreshToken

class BlacklistTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh_token']
        return attrs

    def save(self, **kwargs):
        try:
            # Use the refresh token to blacklist it
            token = RefreshToken(self.token)
            token.blacklist()
        except Exception as e:
            self.fail('bad_token')



class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['name']

    def create(self, validated_data):
        # Create skills and associate them with the user
        print("here skills", validated_data)
        return Skill.objects.create(**validated_data)

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['degree', 'institution', 'field', 'start_date', 'end_date', 'description']

    def create(self, validated_data):
        # Create education and associate it with the user
        education = Education.objects.create(**validated_data)
        return education

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['job_title', 'company', 'location', 'start_date', 'end_date', 'responsibilities']

    def create(self, validated_data):
        # Create experience and associate with the user
        return Experience.objects.create(**validated_data)

class DesiredJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesiredJob
        fields = ['job_title', 'job_location', 'salary_expectation', 'contract_type', 'job_type', 'work_preference', 'description']

    def create(self, validated_data):
        # Create desired job and associate with the user
        return DesiredJob.objects.create(**validated_data)

class PlatformUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    unique_id = serializers.CharField(read_only=True)

    # Add nested serializers
    skills = SkillSerializer(many=True, read_only=True)
    educations = EducationSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)

    class Meta:
        model = PlatformUser
        fields = [
            'id', 'username', 'unique_id', 'email', 'password', 'name', 'country',
            'city', 'phone', 'description', 'role', 'github_link', 'linkedin_link',
            'portfolio_link', 'proficiency',  'gender', 'birth_Date', 'educations', 'skills', 'experiences'
        ]

    def create(self, validated_data):
        # Handle password and unique_id creation
        validated_data['unique_id'] = str(uuid.uuid4())[:11]  # Generates a unique ID (first 11 characters of UUID)
        password = validated_data.pop('password')
        
        # Extract related data for nested serializers
        educations_data = validated_data.pop('educations', [])
        skills_data = validated_data.pop('skills', [])
        experiences_data = validated_data.pop('experiences', [])

        # Create the user
        user = PlatformUser(**validated_data)
        user.set_password(password)
        user.save()

        # Create related fields (skills, educations, experiences)
        for education_data in educations_data:
            Education.objects.create(user=user, **education_data)
        
        for skill_data in skills_data:
            Skill.objects.create(user=user, **skill_data)
        
        for experience_data in experiences_data:
            Experience.objects.create(user=user, **experience_data)

        return user

    def update(self, instance, validated_data):
        # Handle password separately if provided
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        # Update related fields
        educations_data = validated_data.pop('educations', [])
        skills_data = validated_data.pop('skills', [])
        experiences_data = validated_data.pop('experiences', [])

        # Update the user
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Clear and update related fields (if any data was passed for them)
        if educations_data:
            instance.educations.all().delete()  # Clear old educations
            for education_data in educations_data:
                Education.objects.create(user=instance, **education_data)
        
        if skills_data:
            instance.skills.all().delete()  # Clear old skills
            for skill_data in skills_data:
                Skill.objects.create(user=instance, **skill_data)
        
        if experiences_data:
            instance.experiences.all().delete()  # Clear old experiences
            for experience_data in experiences_data:
                Experience.objects.create(user=instance, **experience_data)

        return instance