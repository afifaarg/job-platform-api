# Generated by Django 4.2.5 on 2024-11-19 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobrecruitementAPI', '0020_alter_education_start_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='platformuser',
            name='city',
        ),
        migrations.RemoveField(
            model_name='platformuser',
            name='country',
        ),
        migrations.RemoveField(
            model_name='platformuser',
            name='current_address',
        ),
        migrations.RemoveField(
            model_name='platformuser',
            name='permanent_address',
        ),
        migrations.RemoveField(
            model_name='platformuser',
            name='pin_code',
        ),
        migrations.RemoveField(
            model_name='platformuser',
            name='state',
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_line1', models.TextField(blank=True, default='', null=True)),
                ('address_line2', models.TextField(blank=True, default='', null=True)),
                ('city', models.CharField(blank=True, default='', max_length=250, null=True)),
                ('state', models.CharField(blank=True, default='', max_length=250, null=True)),
                ('country', models.CharField(blank=True, default='', max_length=250, null=True)),
                ('pin_code', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('address_type', models.CharField(choices=[('current', 'Current'), ('permanent', 'Permanent')], default='current', max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='jobrecruitementAPI.platformuser')),
            ],
        ),
    ]
