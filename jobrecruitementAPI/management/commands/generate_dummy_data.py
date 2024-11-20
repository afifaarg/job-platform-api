import random
import json
from faker import Faker
from django.core.management.base import BaseCommand
from jobrecruitementAPI.models import PlatformUser, Address, Skill, Experience, Education, Project

fake = Faker()

CONTRACT_CHOICES = ["internship", "cdd", "cdi"]
JOBTYPE_CHOICES = ["fulltime", "parttime"]
WORK_PREFERENCE_CHOICES = ["remote", "on_site", "hybrid"]

class Command(BaseCommand):
    help = "Generate dummy data for all models and export usernames and passwords"

    def add_arguments(self, parser):
        parser.add_argument("--rows", type=int, default=1000, help="Number of users to generate")
        parser.add_argument("--output", type=str, default="user_credentials.json", help="Output JSON file")

    def handle(self, *args, **options):
        rows = options["rows"]
        output_file = options["output"]

        user_credentials = []
        generated_usernames = set()  # Track unique usernames
        generated_unique_ids = set()  # Track unique IDs

        for _ in range(rows):
            # Ensure unique username
            username = fake.user_name()
            while username in generated_usernames:
                username = f"{fake.user_name()}{random.randint(1, 9999)}"
            generated_usernames.add(username)

            # Ensure unique unique_id
            unique_id = f"E{random.randint(10000000, 99999999)}{random.randint(10, 99)}"
            while unique_id in generated_unique_ids:
                unique_id = f"E{random.randint(10000000, 99999999)}{random.randint(10, 99)}"
            generated_unique_ids.add(unique_id)

            password = fake.password(length=10)
            user = PlatformUser.objects.create_user(
                username=username,
                email=fake.email(),
                password=password,
                name=fake.name(),
                role="employee",
                phone=fake.phone_number(),
                gender=random.choice(["male", "female"]),
                birth_date=fake.date_of_birth(minimum_age=20, maximum_age=60),
                unique_id=unique_id,  # Assign the unique_id
            )
            user_credentials.append({
                "username": username,
                "password": password,
                "unique_id": unique_id,
            })

            # Generate Addresses
            for _ in range(random.randint(1, 2)):
                Address.objects.create(
                    user=user,
                    address_line1=fake.street_address(),
                    city=fake.city(),
                    state=fake.state(),
                    country=fake.country(),
                    pin_code=fake.zipcode(),
                    address_type=random.choice(["current", "permanent"]),
                )

            # Generate Skills
            for _ in range(random.randint(2, 5)):
                Skill.objects.create(user=user, name=fake.job())

            # Generate Experiences
            for _ in range(random.randint(1, 3)):
                start_date = fake.date_between(start_date="-10y", end_date="-1y")
                end_date = fake.date_between(start_date=start_date, end_date="today")
                Experience.objects.create(
                    user=user,
                    job_title=fake.job(),
                    company=fake.company(),
                    location=fake.city(),
                    start_date=start_date,
                    end_date=end_date if random.choice([True, False]) else None,
                    employment_type=random.choice(JOBTYPE_CHOICES),
                    responsibilities=fake.text(max_nb_chars=200),
                    job_summary=fake.text(max_nb_chars=200),
                    primary_skills=fake.text(max_nb_chars=100),
                    tools_technologies=fake.text(max_nb_chars=100),
                    annual_salary=random.randint(50000, 200000),
                )

            # Generate Education
            for _ in range(random.randint(1, 3)):
                Education.objects.create(
                    user=user,
                    degree=fake.random_element(elements=["Bachelor's", "Master's", "PhD"]),
                    institution=fake.company(),
                    field=fake.job(),
                    education_level=random.choice(["Undergraduate", "Postgraduate"]),
                    board=fake.word(),
                    passing_out_year=fake.year(),
                    school_medium=fake.random_element(elements=["English", "French", "Arabic"]),
                    start_date=fake.date_between(start_date="-10y", end_date="-5y"),
                    end_date=fake.date_between(start_date="-5y", end_date="today"),
                )

            # Generate Projects
            for _ in range(random.randint(1, 3)):
                Project.objects.create(
                    user=user,
                    project_title=fake.sentence(nb_words=3),
                    project_summary=fake.text(max_nb_chars=200),
                    project_link=fake.url(),
                )

        # Write user credentials to JSON file
        with open(output_file, "w") as json_file:
            json.dump(user_credentials, json_file, indent=4)

        self.stdout.write(self.style.SUCCESS(f"Successfully generated data for {rows} users and related models!"))
        self.stdout.write(self.style.SUCCESS(f"User credentials saved to {output_file}"))
