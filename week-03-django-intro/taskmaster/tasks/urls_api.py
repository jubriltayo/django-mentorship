from rest_framework.routers import DefaultRouter
from . import views_api

router = DefaultRouter()
router.register('tasks', views_api.TaskViewSet, basename='task')
router.register('categories', views_api.CategoryViewSet, basename='category')
router.register('tags', views_api.TagViewSet, basename='tag')

urlpatterns = router.urls