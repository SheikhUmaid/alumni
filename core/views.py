from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import User, Profile, Job, Mentorship, Application, Event, Notification
from .forms import CustomUserCreationForm, JobForm, MentorshipForm, EventForm, ProfileForm

# --- Access Control Mixins ---
class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = []
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in self.allowed_roles

class StudentRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['student']

class AlumniRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['alumni']

class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['admin']

# --- Auth Views ---
class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Profile is created by signal, update it with branch
        if self.object.role == 'student':
            branch = form.cleaned_data.get('branch')
            if branch:
                self.object.profile.branch = branch
                self.object.profile.save()
        elif self.object.role == 'alumni':
            grad_year = form.cleaned_data.get('graduation_year')
            if grad_year:
                self.object.profile.graduation_year = grad_year
                self.object.profile.save()
        messages.success(self.request, "Account created! Please login.")
        return response

class ProfileUpdateView(LoginRequiredMixin, StudentRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'auth/profile_form.html'
    success_url = reverse_lazy('student_dashboard')

    def get_object(self):
        return self.request.user.profile

class HomeView(TemplateView):
    template_name = 'landing.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == 'student':
                return redirect('student_dashboard')
            elif request.user.role == 'alumni':
                return redirect('alumni_dashboard')
            elif request.user.role == 'admin':
                return redirect('admin_dashboard')
        return super().dispatch(request, *args, **kwargs)

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.role == 'student':
            return reverse_lazy('student_dashboard')
        elif user.role == 'alumni':
            return reverse_lazy('alumni_dashboard')
        elif user.role == 'admin':
            return reverse_lazy('admin_dashboard')
        return super().get_success_url()

# --- Dashboards ---
class StudentDashboardView(LoginRequiredMixin, StudentRequiredMixin, TemplateView):
    template_name = 'dashboards/student.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['applications'] = Application.objects.filter(student=self.request.user)
        ctx['recent_jobs'] = Job.objects.filter(is_verified=True).order_by('-created_at')[:5]
        return ctx

class AlumniDashboardView(LoginRequiredMixin, AlumniRequiredMixin, TemplateView):
    template_name = 'dashboards/alumni.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['posted_jobs'] = Job.objects.filter(posted_by=self.request.user)
        ctx['mentorship'] = Mentorship.objects.filter(mentor=self.request.user).first()
        return ctx

class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'dashboards/admin.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['pending_users'] = User.objects.filter(is_verified=False)
        ctx['pending_jobs'] = Job.objects.filter(is_verified=False)
        
        # KPI Stats
        ctx['total_students'] = User.objects.filter(role='student').count()
        ctx['total_alumni'] = User.objects.filter(role='alumni').count()
        ctx['total_jobs'] = Job.objects.count()
        ctx['verified_jobs'] = Job.objects.filter(is_verified=True).count()
        
        # Chart Data (Mocking some distribution for UI demo)
        ctx['branch_distribution'] = {
            'CSE': Profile.objects.filter(branch='CSE').count(),
            'ECE': Profile.objects.filter(branch='ECE').count(),
            'ME': Profile.objects.filter(branch='ME').count(),
            'CE': Profile.objects.filter(branch='CE').count(),
            'EE': Profile.objects.filter(branch='EE').count(),
        }
        return ctx

# --- Jobs ---
class JobListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = 'jobs/list.html'
    context_object_name = 'jobs'
    
    def get_queryset(self):
        queryset = Job.objects.filter(is_verified=True)
        branch_param = self.request.GET.get('branch')
        
        if branch_param:
            queryset = queryset.filter(branch=branch_param)
        elif branch_param is None:
            # Default to student's branch if no filter is applied
            if self.request.user.is_authenticated and self.request.user.role == 'student':
                try:
                    user_branch = self.request.user.profile.branch
                    if user_branch:
                        queryset = queryset.filter(branch=user_branch)
                except Profile.DoesNotExist:
                    pass
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Determine current branch for UI selection
        branch_param = self.request.GET.get('branch')
        current_branch = ''
        if branch_param:
            current_branch = branch_param
        elif branch_param is None:
             if self.request.user.is_authenticated and self.request.user.role == 'student':
                try:
                    current_branch = self.request.user.profile.branch
                except Profile.DoesNotExist:
                    pass
        context['current_branch'] = current_branch
        print(f"********************{current_branch}***************************")
        return context

class JobCreateView(LoginRequiredMixin, AlumniRequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/form.html'
    success_url = reverse_lazy('alumni_dashboard')

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        messages.success(self.request, "Job posted! Pending admin verification.")
        return super().form_valid(form)

class JobDetailView(LoginRequiredMixin, DetailView):
    model = Job
    template_name = 'jobs/detail.html'

def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.user.role != 'student':
        messages.error(request, "Only students can apply.")
        return redirect('job_list')
    
    if Application.objects.filter(student=request.user, job=job).exists():
        messages.warning(request, "You have already applied.")
        return redirect('job_detail', pk=pk)
    
    Application.objects.create(student=request.user, job=job)
    messages.success(request, "Applied successfully!")
    return redirect('student_dashboard')

# --- Mentorship ---
class MentorshipListView(LoginRequiredMixin, ListView):
    model = Mentorship
    template_name = 'mentorship/list.html'
    context_object_name = 'mentors'

class MentorshipCreateView(LoginRequiredMixin, AlumniRequiredMixin, CreateView):
    model = Mentorship
    form_class = MentorshipForm
    template_name = 'mentorship/form.html'
    success_url = reverse_lazy('alumni_dashboard')

    def form_valid(self, form):
        form.instance.mentor = self.request.user
        return super().form_valid(form)

# --- Events ---
class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events/list.html'
    context_object_name = 'events'

class EventCreateView(LoginRequiredMixin, CreateView): # Admin or Alumni
    model = Event
    form_class = EventForm
    template_name = 'events/form.html'
    success_url = reverse_lazy('event_list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ['admin', 'alumni']:
             return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

# --- Admin Actions ---
def verify_user_action(request, pk):
    if not request.user.role == 'admin': return redirect('home')
    user = get_object_or_404(User, pk=pk)
    user.is_verified = True
    user.save()
    messages.success(request, f"User {user.username} verified.")
    return redirect('admin_dashboard')

def verify_job_action(request, pk):
    if not request.user.role == 'admin': return redirect('home')
    job = get_object_or_404(Job, pk=pk)
    job.is_verified = True
    job.save()
    messages.success(request, "Job verified.")
    return redirect('admin_dashboard')
