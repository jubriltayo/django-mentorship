from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django.core.cache import cache

from .models import Task, Category, Tag
from .serializers import TaskSerializer, CategorySerializer, TagSerializer
from .tasks import send_task_reminder, generate_report


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            owner=self.request.user
        ).select_related('category').prefetch_related('tags')

    def perform_create(self, serializer):
        task = serializer.save(owner=self.request.user)
        send_task_reminder.delay(task.id)
        self._invalidate_task_cache(self.request.user.id)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.mark_complete()
        generate_report.delay(request.user.id)
        self._invalidate_task_cache(request.user.id)
        return Response({'status': 'completed'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        user_id = request.user.id
        cache_key = f"task_stats_{user_id}"

        data = cache.get(cache_key)

        if data is None:
            queryset = self.get_queryset()
        
            data = {
                'total': queryset.count(),
                'completed': queryset.filter(status='completed').count(),
                'pending': queryset.filter(status='pending').count(),
            }
        
            cache.set(cache_key, data, timeout=60)

        return Response(data)

    def _invalidate_task_cache(self, user_id):
        cache.delete(f"task_stats_{user_id}")


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.annotate(task_count=Count('tasks'))
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
