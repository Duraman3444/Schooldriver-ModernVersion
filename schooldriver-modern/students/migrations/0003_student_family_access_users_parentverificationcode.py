# Generated by Django 4.2.16 on 2025-07-24 20:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('students', '0002_alter_emergencycontact_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='family_access_users',
            field=models.ManyToManyField(blank=True, help_text="Parent/Guardian users who can access this student's information via the parent portal", related_name='accessible_students', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ParentVerificationCode',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(editable=False, max_length=8, unique=True)),
                ('parent_email', models.EmailField(help_text='Email address of the parent requesting access', max_length=254)),
                ('parent_name', models.CharField(help_text='Full name of the parent requesting access', max_length=200)),
                ('is_used', models.BooleanField(default=False)),
                ('used_at', models.DateTimeField(blank=True, null=True)),
                ('expires_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, help_text='Administrative notes about this verification request')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_verification_codes', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verification_codes', to='students.student')),
                ('used_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='used_verification_codes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['code'], name='students_pa_code_b588b2_idx'), models.Index(fields=['parent_email'], name='students_pa_parent__478986_idx'), models.Index(fields=['expires_at'], name='students_pa_expires_fb3513_idx')],
            },
        ),
    ]
