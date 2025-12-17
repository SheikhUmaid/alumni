from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('alumni', 'Alumni'),
        ('admin', 'Admin'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    is_verified = models.BooleanField(default=False)
    # is_active and date_joined (created_at) are already in AbstractUser

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

class Profile(models.Model):
    BRANCH_CHOICES = (
        ('CSE', 'Computer Science and Engineering'),
        ('ECE', 'Electronics and Communication Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('EE', 'Electrical Engineering'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.CharField(max_length=100, blank=True)
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    skills = models.TextField(blank=True, help_text="Comma separated skills")
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    company = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Job(models.Model):
    JOB_TYPE_CHOICES = (
        ('internship', 'Internship'),
        ('fulltime', 'Full-time'),
    )
    BRANCH_CHOICES = (
        ('CSE', 'Computer Science and Engineering'),
        ('ECE', 'Electronics and Communication Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('EE', 'Electrical Engineering'),
    )
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    company = models.CharField(max_length=100)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES, blank=True, help_text="Relevant branch for this job")
    location = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Mentorship(models.Model):
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentorships')
    expertise_areas = models.CharField(max_length=255)
    availability = models.CharField(max_length=200, help_text="e.g. Weekends 10-12 PM")
    max_mentees = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Mentorship by {self.mentor.get_full_name()}"

class Application(models.Model):
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} applied for {self.job.title}"

class Event(models.Model):
    MODE_CHOICES = (
        ('online', 'Online'),
        ('offline', 'Offline'),
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_time = models.DateTimeField()
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    registration_limit = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"
