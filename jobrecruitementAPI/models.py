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

GENDER_CHOICES = [
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
    phone = models.CharField(max_length=150, default="", null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    gender = models.CharField(max_length=30, choices=GENDER_CHOICES, default="", null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default="employee", null=True, blank=True)
    adhaar_number = models.CharField(max_length=12, null=True, blank=True)
    disability_status = models.BooleanField(default=False)
    govt_employee = models.BooleanField(default=False)
    ex_military = models.BooleanField(default=False)
    reserve_forces = models.BooleanField(default=False)
    military = models.BooleanField(default=False)
    current_ctc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expected_ctc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return self.username

    @property
    def total_years_of_experience(self):
        total_years = 0
        for experience in self.experiences.all():
            end_date = experience.end_date or timezone.now().date()
            years = (end_date - experience.start_date).days / 365.25
            total_years += years
        return round(total_years, 0)

class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ('current', 'Current'),
        ('permanent', 'Permanent'),
    ]
    
    user = models.ForeignKey('PlatformUser', on_delete=models.CASCADE, related_name='addresses')
    address_line1 = models.TextField(default="", null=True, blank=True)
    address_line2 = models.TextField(default="", null=True, blank=True)
    city = models.CharField(max_length=250, default="", null=True, blank=True)
    state = models.CharField(max_length=250, default="", null=True, blank=True)
    country = models.CharField(max_length=250, default="", null=True, blank=True)
    pin_code = models.CharField(max_length=20, default="", null=True, blank=True)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='current')

    def __str__(self):
        return f"{self.user.name} - {self.address_type}"
    
class Skill(models.Model):
    user = models.ForeignKey(PlatformUser, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Experience(models.Model):
    user = models.ForeignKey(PlatformUser, on_delete=models.CASCADE, related_name="experiences")
    job_title = models.CharField(max_length=150, default="", blank=True, null=True)
    company = models.CharField(max_length=150)
    location = models.CharField(max_length=150, default="")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    employment_type = models.CharField(max_length=45, default="", blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    job_summary = models.TextField(blank=True, null=True)
    primary_skills = models.TextField(blank=True, null=True)
    tools_technologies = models.TextField(blank=True, null=True)
    domain_knowledge = models.TextField(blank=True, null=True)
    annual_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fixed_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    variable_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currently_working = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.job_title} at {self.company}"

class Education(models.Model):
    user = models.ForeignKey(PlatformUser, on_delete=models.CASCADE, related_name="educations")
    degree = models.CharField(max_length=150)
    institution = models.CharField(max_length=150)
    field = models.CharField(max_length=150, default="")
    education_level = models.CharField(max_length=100, blank=True, null=True)  # New field
    board = models.CharField(max_length=100, blank=True, null=True)
    passing_out_year = models.CharField(max_length=4, blank=True, null=True)
    school_medium = models.CharField(max_length=100, blank=True, null=True)
    grading_system = models.CharField(max_length=100, blank=True, null=True)
    total_marks = models.CharField(max_length=50, blank=True, null=True)
    course_type = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    still_studying = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.degree} from {self.institution}"

class Project(models.Model):
    user = models.ForeignKey(PlatformUser, on_delete=models.CASCADE, related_name="projects")
    project_title = models.CharField(max_length=150)
    project_summary = models.TextField(blank=True, null=True)
    project_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.project_title
