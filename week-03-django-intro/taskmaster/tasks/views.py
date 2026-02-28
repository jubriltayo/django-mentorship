# ==========================
# FUNCTION BASED VIEW (FBV)
# ==========================

from django.http import (
    HttpRequest,
    HttpResponse,
    JsonResponse,
    HttpResponseRedirect,
    Http404,
    HttpResponseBadRequest,
)
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.core.paginator import Paginator

from .models import Task, Category, Status, Priority


# Basic view
def task_list(request: HttpRequest) -> HttpResponse:
    """List all tasks with filtering and pagination"""
    tasks = Task.objects.select_related("category").prefetch_related("tags")

    # Filter by status (query parameter)
    status = request.GET.get("status")
    if status:
        tasks = tasks.filter(status=status)

    # Filter by category
    category_id = request.GET.get("category")
    if category_id:
        tasks = tasks.filter(category_id=category_id)

    # Pagination
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "statuses": Status.choices,
        "current_status": status,
        "current_category": category_id,
    }

    return render(request, "tasks/task_list.html", context)


# Detail view with 404 handling
def task_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Show task details"""
    task = get_object_or_404(Task, pk=pk)
    return render(request, "tasks/task_detail.html", {"task": task})


# Handle multiple HTTP methods
@require_http_methods(["GET", "POST"])
def task_create(request: HttpRequest) -> HttpResponse:
    """Create a new task"""
    if request.method == "POST":

        # Process form data
        title = request.POST.get("title")
        description = request.POST.get("description", "")
        priority = request.POST.get("priority", Priority.MEDIUM)
        category_id = request.POST.get("category")

        # Validation
        if not title:
            return render(
                request,
                "tasks/task_form.html",
                {"error": "Title is required", "categories": Category.objects.all()},
            )

        # Create task
        task = Task.objects.create(
            title=title,
            description=description,
            priority=priority,
            category_id=category_id if category_id else None,
        )

        # Redirect to detail page
        return redirect("tasks:task_detail", pk=task.pk)

    # GET request - show form
    return render(
        request,
        "tasks/task_form.html",
        {
            "categories": Category.objects.all(),
            "priorities": Priority.choices,
        },
    )


# JSON response for API-like endpoints
def task_api_list(request: HttpRequest) -> HttpResponse:
    """Return tasks as JSON"""
    tasks = Task.objects.all().values("id", "title", "status", "priority", "created_at")
    return JsonResponse({"tasks": list(tasks)})


# Update with method restriction
@require_POST
def task_complete(request: HttpRequest, pk: int) -> HttpResponse:
    """Mark a task as complete"""
    task = get_object_or_404(Task, pk=pk)
    task.mark_completed()

    # Check if AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"status": "success", "task_id": pk})

    return redirect("tasks:task_detail", pk=pk)


# Delete with confirmation
@require_http_methods(["GET", "POST"])
def task_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete a task"""
    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":
        task.delete()
        return redirect("tasks:task_list")

    return render(request, "tasks/task_confirm_delete.html", {"task": task})


# ========================
# CLASS BASED VIEW (CBV)
# ========================

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
# from django.urls import reverse_lazy
# from django.contrib import messages
from django.db.models import Count

# from .models import Task, Category, Status, Priority


# class TaskListView(ListView):
#     model = Task
#     template_name = "tasks/task_list.html"
#     context_object_name = "tasks"
#     paginate_by = 10

#     def get_queryset(self):
#         """Filter queryset based on query parameters"""
#         queryset = Task.objects.select_related("category").prefetch_related("tags")

#         status = self.request.GET.get("status")
#         if status:
#             queryset = queryset.filter(status=status)

#         category = self.request.GET.get("category")
#         if category:
#             queryset = queryset.filter(category_id=category)

#         return queryset

#     def get_context_data(self, **kwargs):
#         """Add extra context"""
#         context = super().get_context_data(**kwargs)
#         context["categories"] = Category.objects.all()
#         context["statuses"] = Status.choices
#         return context


# class TaskDetailView(DetailView):
#     model = Task
#     template_name = "tasks/task_detail.html"
#     context_object_name = "task"

#     def get_queryset(self):
#         """Optimize query with related objects"""
#         return Task.objects.select_related("category").prefetch_related("tags")


# class TaskCreateView(CreateView):
#     "Create a new task"

#     model = Task
#     template_name = "tasks/task_form.html"
#     fields = [
#         "title",
#         "description",
#         "priority",
#         "status",
#         "category",
#         "due_date",
#         "tags",
#     ]

#     def get_success_url(self):
#         return reverse_lazy("tasks:task_detail", kwargs={"pk": self.object.pk})

#     def form_valid(self, form):
#         messages.success(self.request, "Task created successfully!")
#         return super().form_valid(form)


class TaskUpdateView(UpdateView):
    """Update an existing task."""

    model = Task
    template_name = "tasks/task_form.html"
    fields = [
        "title",
        "description",
        "priority",
        "status",
        "category",
        "due_date",
        "tags",
    ]

    def get_success_url(self):
        return reverse_lazy("tasks:task_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Task updated successfully!")
        return super().form_valid(form)


# class TaskDeleteView(DeleteView):
#     """Delete a task."""

#     model = Task
#     template_name = "tasks/task_confirm_delete.html"
#     success_url = reverse_lazy("tasks:task_list")

#     def form_valid(self, form):
#         messages.success(self.request, "Task deleted successfully!")
#         return super().form_valid(form)


class DashboardView(TemplateView):
    """Dashboard with statistics."""

    template_name = "tasks/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_tasks"] = Task.objects.count()
        context["completed_tasks"] = Task.objects.filter(
            status=Status.COMPLETED
        ).count()
        context["pending_tasks"] = Task.objects.filter(status=Status.PENDING).count()
        context["categories"] = Category.objects.annotate(task_count=Count("tasks"))
        return context
