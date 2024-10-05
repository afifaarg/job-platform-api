from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

CONTRACT_CHOICES = [
        ("internship", "Internship"),
        ("cdd", "CDD"),
        ("cdi", "CDI"),
    ]
    
JOBTYPE_CHOICES = [
    ("fulltime", "Full-time"),
    ("parttime", "Part-time"),
]

WORK_PREFERENCE_CHOICES = [
    ("remote", "Remote"),
    ("on_site", "On-site"),
    ("hybrid", "Hybrid"),
]

gender_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
]
class PlatformUser(User):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("employee", "Employee"),
    ]
    
    unique_id = models.CharField(max_length=11, unique=True, null=True, blank=True)
    name = models.CharField(max_length=150)
    country = models.CharField(max_length=250, default="" , null=True, blank=True)
    description = models.TextField(default="", null=True, blank=True)
    city = models.CharField(max_length=250, default="", null=True, blank=True)
    phone = models.CharField(max_length=150, default="", null=True, blank=True)
    github_link = models.CharField(max_length=250, default="", null=True, blank=True)
    linkedin_link = models.CharField(max_length=250, default="", null=True, blank=True)
    portfolio_link = models.CharField(max_length=250, default="", null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    resume_file = models.FileField(upload_to='resumes/', null=True, blank=True)
    gender = models.CharField(max_length=30, choices=gender_CHOICES, default="", null=True, blank=True)
    birth_Date = models.DateField(default="1999-01-01", null=True, blank=True)
    proficiency = models.CharField(max_length=250, default="", null=True, blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default="employee", null=True, blank=True)

    def __str__(self):
        return self.username


    @property
    def total_years_of_experience(self):
        total_years = 0
        for experience in self.experiences.all():
            # Calculate the end date; use current date if end_date is None
            end_date = experience.end_date or timezone.now().date()
            # Calculate the difference in years
            years = (end_date - experience.start_date).days / 365.25  # accounting for leap years
            total_years += years
        return round(total_years, 0)  # Round to 2 decimal places
    
class DesiredJob(models.Model):
    user = models.ForeignKey(PlatformUser, on_delete=models.CASCADE, related_name="desired_job", default=None, blank=True, null=True)
    job_title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    salary_expectation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    job_location = models.CharField(max_length=150, blank=True, null=True, default="")
    
    contract_type = models.CharField(max_length=20, choices=CONTRACT_CHOICES, blank=True, null=True, default="cdi")
    job_type = models.CharField(max_length=20, choices=JOBTYPE_CHOICES, blank=True, null=True, default="fulltime")
    work_preference = models.CharField(max_length=20, choices=WORK_PREFERENCE_CHOICES, blank=True, null=True, default="on_site")
    
    def __str__(self):
        return self.job_title

class Skill(models.Model):
    user = models.ForeignKey(PlatformUser, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=100, unique=False)

    def __str__(self):
        return self.name
    
class Experience(models.Model):
    user = models.ForeignKey(PlatformUser, on_delete=models.CASCADE, related_name="experiences")
    job_title = models.CharField(max_length=150)
    company = models.CharField(max_length=150)
    location = models.CharField(max_length=150, default="")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # Null if currently employed
    responsibilities = models.TextField(blank=True, null=True)
    job_type = models.CharField(max_length=20, choices=JOBTYPE_CHOICES, blank=True, null=True, default="fulltime")
    def __str__(self):
        return f"{self.job_title} at {self.company}"

class Education(models.Model):
    user = models.ForeignKey(PlatformUser, on_delete=models.CASCADE, related_name="educations")
    degree = models.CharField(max_length=150)
    institution = models.CharField(max_length=150)
    field = models.CharField(max_length=150, default="")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # Can be null for ongoing education
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.degree} from {self.institution}"

