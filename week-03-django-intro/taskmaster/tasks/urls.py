from django.urls import path, re_path, include
from . import views
from . import converters

app_name = "tasks"

register_converter(converters.FourDigitYearConverter, "yyyy")

urlpatterns = [
    # Function Based Views (FBV)
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/create/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/", views.task_detail, name="task_detail"),
    path("tasks/<int:pk>/complete/", views.task_complete, name="task_complete"),
    path("tasks/<int:pk>/delete/", views.task_delete, name="task_delete"),
    # Class Based Views (CBV) - Alternative
    # path("tasks/", views.TaskListView.as_view(), name="task_list"),
    # path("tasks/create/", views.TaskCreateView.as_view(), name="task_create"),
    # path("tasks/<int:pk>/", views.TaskDetailView.as_view(), name="task_detail"),
    # path("tasks/<int:pk>/edit/", views.TaskUpdateView.as_view(), name="task_update"),
    # path("tasks/<int:pk>/delete/", views.TaskDeleteView.as_view(), name="task_delete"),
    # Slug Based URLs
    # path("category/<slug:slug>/"), views.category_detail, name="category_detail",
    # Multiple parameters
    path("archive/<int:year>/<int:month>/", views.archive, name="archive"),
    # path("archive/<yyyy:year>/", views.archive, name="archive"),
    # API endpoints
    path("api/tasks/", views.task_api_list, name="api_task_list"),
    path("api/tasks/<int:pk>/", views.task_api_detail, name="api_task_detail"),
]
