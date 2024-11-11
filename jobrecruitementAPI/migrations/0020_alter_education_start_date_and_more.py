# Generated by Django 4.2.5 on 2024-11-11 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobrecruitementAPI', '0019_remove_education_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='education',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='experience',
            name='employment_type',
            field=models.CharField(blank=True, default='', max_length=45, null=True),
        ),
        migrations.AlterField(
            model_name='experience',
            name='job_title',
            field=models.CharField(blank=True, default='', max_length=150, null=True),
        ),
    ]