from tokenize import TokenError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken  # Optional, for JWT
from django.contrib.auth.models import User
from rest_framework import viewsets
from .models import PlatformUser, DesiredJob
from .serializers import PlatformUserSerializer, BlacklistTokenSerializer, SkillSerializer, EducationSerializer, ExperienceSerializer, DesiredJobSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view
from django.core.validators import validate_email

@api_view(['POST'])
def register_admin(request):
    if request.method == 'POST':
        data = request.data
        username = data.get('username')
        name = data.get('name')
        email = data.get('email')
        gender = data.get('gender')
        password = data.get('password')

        # Validate required fields
        if not username or not name or not email or not gender or not password:
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)

        # Check for existing user
        if PlatformUser.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        if PlatformUser.objects.filter(email=email).exists():
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create and save the new PlatformUser object
        platform_user = PlatformUser(
            username=username,
            email=email,
            name=name,
            gender=gender,
            role='admin'  # Set the role to admin
        )
        platform_user.set_password(password)  # Hash the password
        platform_user.save()  # Save the user to the database
        
        return Response({"message": "Admin user registered successfully."}, status=status.HTTP_201_CREATED)
    
class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh_token")  # Get refresh token from the request body
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class PlatformUserViewSet(viewsets.ModelViewSet):
    queryset = PlatformUser.objects.all()
    serializer_class = PlatformUserSerializer

    @transaction.atomic  # Ensure that all saves are part of the same transaction
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True) 
        # Ensure required fields are present
        if not all([
            'username' in request.data,
            'password' in request.data,
            'name' in request.data,
        ]):
            return Response({'error': 'Missing required fields: username, password, name'}, status=status.HTTP_400_BAD_REQUEST)

        # Save the main user profile
        user = serializer.save()
        # Handle related models: skills, education, experience, and desired job
        if 'skills' in request.data:
            print("skills")
            # Convert the list of skill strings to a list of dictionaries with the 'name' key
            skills_data = [{'name': skill} for skill in request.data['skills']]
            skills_serializer = SkillSerializer(data=skills_data, many=True)
            if skills_serializer.is_valid(raise_exception=True):
                skills_serializer.save(user=user)  # Save related skills

        if 'educations' in request.data:
            educations_serializer = EducationSerializer(data=request.data['educations'], many=True)
            if educations_serializer.is_valid(raise_exception=True):
                educations_serializer.save(user=user)  # Save related educations

        if 'experiences' in request.data:
            experiences_serializer = ExperienceSerializer(data=request.data['experiences'], many=True)
            if experiences_serializer.is_valid(raise_exception=True):
                experiences_serializer.save(user=user)  # Save related experiences

        if 'desired_job' in request.data:
            desired_job_serializer = DesiredJobSerializer(data=request.data['desired_job'])
            if desired_job_serializer.is_valid(raise_exception=True):
                desired_job_serializer.save(user=user)  # Save related desired job

        # Generate JWT tokens for the user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "user": PlatformUserSerializer(user).data,
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
            "message": "User registered successfully"
        }, status=status.HTTP_201_CREATED)

    @transaction.atomic  # Ensure that all saves are part of the same transaction
    def update(self, request, *args, **kwargs):
        instance = self.get_object()  # Get the current user instance
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        user = serializer.save()


        # Handle related models: skills, education, experience, and desired job
        if 'skills' in request.data:
            user.skills.all().delete() 
            skills_data = [{'name': skill} for skill in request.data['skills']]
            skills_serializer = SkillSerializer(data=skills_data, many=True)
            if skills_serializer.is_valid(raise_exception=True):
                skills_serializer.save(user=user)  # Save related skills

        if 'educations' in request.data:
            user.educations.all().delete()
            educations_serializer = EducationSerializer(data=request.data['educations'], many=True)
            if educations_serializer.is_valid(raise_exception=True):
                educations_serializer.save(user=user)  # Save related educations

        if 'experiences' in request.data:
            user.experiences.all().delete()
            experiences_serializer = ExperienceSerializer(data=request.data['experiences'], many=True)
            if experiences_serializer.is_valid(raise_exception=True):
                experiences_serializer.save(user=user)  # Save related experiences

        if 'desired_job' in request.data:
            user.desired_job.delete() 
            desired_job_serializer = DesiredJobSerializer(data=request.data['desired_job'])
            if desired_job_serializer.is_valid(raise_exception=True):
                desired_job_serializer.save(user=user)  # Save related desired job

        # Generate JWT tokens for the user (if needed)
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": PlatformUserSerializer(user).data,
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
            "message": "User updated successfully"
        }, status=status.HTTP_200_OK)

class LoginView(APIView):
 def post(self, request, *args, **kwargs):
    username = request.data.get("username")
    password = request.data.get("password")

    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if not user:
        print("wrong credentials")
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    # Optional: Generate JWT Token
    refresh = RefreshToken.for_user(user)

    # Fetch user information
    yourInfo = PlatformUser.objects.get(username=username)  # Ensure user is an instance of PlatformUser

    # Prepare response data
    response_data = {
        'role': yourInfo.role,
        'id': yourInfo.id,
    }

    # Check if the user is an admin
    if yourInfo.role == 'admin':
        # Fetch all users' data except admins, if needed
        all_users_data = PlatformUser.objects.exclude(role='admin')  # Adjust based on your requirements
        all_users_response = [
            {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'gender':user.gender,
                'joinedDate': yourInfo.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                'uniqueID':user.unique_id,
                'experienceYears':user.total_years_of_experience,
                'phone': user.phone,
                'country': user.country,
                'city': user.city,
            }
            for user in all_users_data
        ]
        
        
        response_data['all_users'] = all_users_response  # Include all users in the response
    print('here')
    return Response({
        'message': 'Login successful!',
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user_data': response_data
    }, status=status.HTTP_200_OK)