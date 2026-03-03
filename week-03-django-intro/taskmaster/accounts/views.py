# Function-based views
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from tasks.models import Task

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

@permission_required('tasks.add_task')
def task_create(request):
    ...

# Class-based views
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView, DeleteView

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    ...

class TaskDeleteView(PermissionRequiredMixin, DeleteView):
    model = Task
    permission_required = 'tasks.delete_task'