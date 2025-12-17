from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Job, Mentorship, Application, Event, Notification

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_verified', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'is_verified')}),
    )
    actions = ['verify_users']

    def verify_users(self, request, queryset):
        queryset.update(is_verified=True)
    verify_users.short_description = "Verify selected users"

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'posted_by', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'job_type')
    actions = ['verify_jobs']

    def verify_jobs(self, request, queryset):
        queryset.update(is_verified=True)
    verify_jobs.short_description = "Verify selected jobs"

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'status', 'applied_at')
    list_filter = ('status',)

admin.site.register(Profile)
admin.site.register(Mentorship)
admin.site.register(Event)
admin.site.register(Notification)
