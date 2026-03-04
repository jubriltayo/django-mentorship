from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count

from .models import Task, Category, Tag
from .serializers import TaskSerializer, CategorySerializer, TagSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            owner=self.request.user
        ).select_related('category').prefetch_related('tags')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.mark_complete()
        return Response({'status': 'completed'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        return Response({
            'total': queryset.count(),
            'completed': queryset.filter(status='completed').count(),
            'pending': queryset.filter(status='pending').count(),
        })


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.annotate(task_count=Count('tasks'))
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
