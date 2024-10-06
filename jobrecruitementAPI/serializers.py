from rest_framework import serializers  # Importing the serializers module from Django REST Framework
from .models import PlatformUser, Skill, Education, Experience  # Importing the relevant models
import uuid  # Importing the uuid library for unique ID generation
from rest_framework_simplejwt.tokens import RefreshToken  # Importing RefreshToken for token management
import random  # Importing random for generating random numbers
from datetime import datetime  # Importing datetime for handling date and time

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
        return Skill.objects.create(**validated_data)  # Create and return a Skill instance

# Serializer for the Education model
class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education  # Specifying the model to be serialized
        fields = ['degree', 'institution', 'field', 'start_date', 'end_date', 'description']  # Fields to include

    def create(self, validated_data):
        # Create education and associate it with the user
        education = Education.objects.create(**validated_data)  # Create and return an Education instance
        return education

# Serializer for the Experience model
class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience  # Specifying the model to be serialized
        fields = ['job_title', 'company', 'location', 'start_date', 'end_date', 'responsibilities']  # Fields to include

    def create(self, validated_data):
        # Create experience and associate with the user
        return Experience.objects.create(**validated_data)  # Create and return an Experience instance

# Serializer for the PlatformUser model
class PlatformUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Password field that will not be read back
    unique_id = serializers.CharField(read_only=True)  # Unique ID field that can only be read, not written to

    # Nested serializers for related fields
    skills = SkillSerializer(many=True, read_only=True)  # Skills related to the user
    educations = EducationSerializer(many=True, read_only=True)  # Education records related to the user
    experiences = ExperienceSerializer(many=True, read_only=True)  # Experience records related to the user

    class Meta:
        model = PlatformUser  # Specifying the model to be serialized
        fields = [
            'id', 'username', 'unique_id', 'email', 'password', 'name', 'country',
            'city', 'phone', 'description', 'role', 'github_link', 'linkedin_link',
            'portfolio_link', 'proficiency',  'gender', 'birth_Date', 'educations', 'skills', 'experiences'
        ]  # Fields to include in the serialized output

    def create(self, validated_data):
        # Handle unique_id creation
        year = datetime.now().year  # Get current year (YYYY)
        random_digits = str(random.randint(10000, 99999))  # Generate a random 5-digit number
        unique_id = f"EI{year}{random_digits}"  # Combine the parts to create a unique ID
        validated_data['unique_id'] = unique_id  # Adds the generated unique ID to the validated data
        password = validated_data.pop('password')  # Remove password from validated data for processing

        # Extract related data for nested serializers
        educations_data = validated_data.pop('educations', [])  # Pop educations data from validated data
        skills_data = validated_data.pop('skills', [])  # Pop skills data from validated data
        experiences_data = validated_data.pop('experiences', [])  # Pop experiences data from validated data

        # Create the user
        user = PlatformUser(**validated_data)  # Create a PlatformUser instance
        user.set_password(password)  # Hash the password for security
        user.save()  # Save the user instance to the database

        # Create related fields (skills, educations, experiences)
        for education_data in educations_data:  # Loop through each education data
            Education.objects.create(user=user, **education_data)  # Create and associate Education with the user
        
        for skill_data in skills_data:  # Loop through each skill data
            Skill.objects.create(user=user, **skill_data)  # Create and associate Skill with the user
        
        for experience_data in experiences_data:  # Loop through each experience data
            Experience.objects.create(user=user, **experience_data)  # Create and associate Experience with the user

        return user  # Return the created user instance

    def update(self, instance, validated_data):
        # Handle password separately if provided
        password = validated_data.pop('password', None)  # Pop password if it exists
        if password:
            instance.set_password(password)  # Hash the new password if provided

        # Update related fields
        educations_data = validated_data.pop('educations', [])  # Pop educations data from validated data
        skills_data = validated_data.pop('skills', [])  # Pop skills data from validated data
        experiences_data = validated_data.pop('experiences', [])  # Pop experiences data from validated data

        # Update the user instance
        for attr, value in validated_data.items():  # Loop through each attribute in validated data
            setattr(instance, attr, value)  # Update the instance attribute with the new value

        instance.save()  # Save the updated instance to the database

        # Clear and update related fields (if any data was passed for them)
        if educations_data:  # If new education data was provided
            instance.educations.all().delete()  # Clear old educations
            for education_data in educations_data:  # Loop through each new education data
                Education.objects.create(user=instance, **education_data)  # Create and associate new Education with the user
        
        if skills_data:  # If new skills data was provided
            instance.skills.all().delete()  # Clear old skills
            for skill_data in skills_data:  # Loop through each new skill data
                Skill.objects.create(user=instance, **skill_data)  # Create and associate new Skill with the user
        
        if experiences_data:  # If new experiences data was provided
            instance.experiences.all().delete()  # Clear old experiences
            for experience_data in experiences_data:  # Loop through each new experience data
                Experience.objects.create(user=instance, **experience_data)  # Create and associate new Experience with the user

        return instance  # Return the updated instance
