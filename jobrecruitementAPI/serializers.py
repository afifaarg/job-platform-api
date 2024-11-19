from rest_framework import serializers  # Importing the serializers module from Django REST Framework
from .models import PlatformUser, Skill, Education, Experience, Project, Address  # Importing the relevant models
import uuid  # Importing the uuid library for unique ID generation
from rest_framework_simplejwt.tokens import RefreshToken  # Importing RefreshToken for token management
import random  # Importing random for generating random numbers
from datetime import datetime  # Importing datetime for handling date and time
from django.db.models import Max

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
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['address_line1', 'address_line2', 'city', 'state', 'country', 'pin_code', 'address_type']


class PlatformUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    unique_id = serializers.CharField(read_only=True)
    skills = SkillSerializer(many=True, required=False)
    educations = EducationSerializer(many=True, required=False)
    experiences = ExperienceSerializer(many=True, required=False)
    projects = ProjectSerializer(many=True, required=False)
    current_address = AddressSerializer(required=False)
    permanent_address = AddressSerializer(required=False)

    govt_employee = serializers.BooleanField(required=False)
    ex_military = serializers.BooleanField(required=False)
    reserve_forces = serializers.BooleanField(required=False)
    military = serializers.BooleanField(required=False)

    class Meta:
        model = PlatformUser
        fields = [
            'id', 'unique_id', 'username', 'email', 'password', 'name', 
            'phone', 'gender', 'birth_date', 'role', 'adhaar_number',
            'disability_status', 'govt_employee', 'ex_military', 'reserve_forces', 
            'military', 'current_ctc', 'expected_ctc', 'skills', 'educations', 'experiences',
            'projects', 'permanent_address', 'current_address'
        ]
        extra_kwargs = {
            'name': {'required': False},
            'phone': {'required': False},
            'current_address': {'required': False},
            'permanent_address': {'required': False},
            'gender': {'required': False},
            'birth_date': {'required': False},
            'role': {'required': False},
            'adhaar_number': {'required': False},
            'disability_status': {'required': False},
            'current_ctc': {'required': False},
            'expected_ctc': {'required': False},
        }

    def create(self, validated_data):
        # Extract the password and address data
        password = validated_data.pop('password', None)
        current_address_data = validated_data.pop('current_address', None)
        permanent_address_data = validated_data.pop('permanent_address', None)

        # Generate unique_id
        current_year = datetime.now().year % 100  # Get last two digits of the year
        last_unique_id = PlatformUser.objects.aggregate(Max('unique_id'))['unique_id__max']
        if last_unique_id:
            last_sequential = int(last_unique_id[1:8])  # Extract sequential part
            new_sequential = last_sequential + 1
        else:
            new_sequential = 1  # Start with 1 if no users exist
        
        unique_id = f"E{str(new_sequential).zfill(7)}{current_year}"

        # Create user
        user = PlatformUser(
            **validated_data,
            unique_id=unique_id
        )
        if password:
            user.set_password(password)
        user.save()

        # Create address instances
        if current_address_data:
            Address.objects.create(user=user, **current_address_data, address_type='current')
        if permanent_address_data:
            Address.objects.create(user=user, **permanent_address_data, address_type='permanent')

        return user
    def update(self, instance, validated_data):
        # Extract address data
        current_address_data = validated_data.pop('current_address', None)
        permanent_address_data = validated_data.pop('permanent_address', None)
        educations_data = validated_data.pop('educations', [])
        projects_data = validated_data.pop('projects', [])
        skills_data = validated_data.pop('skills', [])
        experiences_data = validated_data.pop('experiences', [])

        # Update simple fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update address data
        if current_address_data:
            current_address = instance.addresses.filter(address_type='current').first()
            if current_address:
                for attr, value in current_address_data.items():
                    setattr(current_address, attr, value)
                current_address.save()
            else:
                Address.objects.create(user=instance, **current_address_data, address_type='current')
        
        if permanent_address_data:
            permanent_address = instance.addresses.filter(address_type='permanent').first()
            if permanent_address:
                for attr, value in permanent_address_data.items():
                    setattr(permanent_address, attr, value)
                permanent_address.save()
            else:
                Address.objects.create(user=instance, **permanent_address_data, address_type='permanent')

        # Update other related data (e.g., educations, skills, experiences)
        instance.projects.all().delete()
        for project in projects_data:
            Project.objects.create(user=instance, **project)

        instance.educations.all().delete()
        for education in educations_data:
            Education.objects.create(user=instance, **education)

        instance.skills.all().delete()
        for skill in skills_data:
            Skill.objects.create(user=instance, **skill)

        instance.experiences.all().delete()
        for experience in experiences_data:
            Experience.objects.create(user=instance, **experience)

        return instance