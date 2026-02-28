"""
Custom template tags and filters for the tasks app.

Usage in templates:
    {% load task_extras %}
    {{ task.status|status_badge }}
    {% task_stats as stats %}
"""

from django import template
from django.utils.html import format_html
from django.db.models import Count

from tasks.models import Task, Status

register = template.Library()


# ============================================================
# FILTERS
# ============================================================

@register.filter
def status_badge(status: str) -> str:
    """
    Return a Bootstrap badge class based on task status.

    Usage: {{ task.status|status_badge }}
    """
    badge_classes = {
        'completed': 'bg-success',
        'in_progress': 'bg-warning text-dark',
        'pending': 'bg-secondary',
        'cancelled': 'bg-danger',
    }
    return badge_classes.get(status, 'bg-secondary')


@register.filter
def priority_stars(priority: int) -> str:
    """
    Display priority as stars.

    Usage: {{ task.priority|priority_stars }}
    """
    return '★' * priority + '☆' * (4 - priority)


@register.filter
def percentage(value, total):
    """
    Calculate percentage.

    Usage: {{ completed|percentage:total }}
    """
    try:
        return int((value / total) * 100)
    except (ValueError, ZeroDivisionError):
        return 0


# ============================================================
# SIMPLE TAGS
# ============================================================

@register.simple_tag
def task_count(status: str = None) -> int:
    """
    Get count of tasks, optionally filtered by status.

    Usage:
        {% task_count as total %}
        {% task_count 'completed' as completed %}
    """
    if status:
        return Task.objects.filter(status=status).count()
    return Task.objects.count()


@register.simple_tag(takes_context=True)
def active_link(context, url_name: str) -> str:
    """
    Return 'active' if current URL matches.

    Usage: <a class="nav-link {% active_link 'tasks:task_list' %}">
    """
    request = context.get('request')
    if request and request.resolver_match:
        if request.resolver_match.url_name == url_name:
            return 'active'
    return ''


# ============================================================
# INCLUSION TAGS
# ============================================================

@register.inclusion_tag('tasks/_task_card.html')
def task_card(task):
    """
    Render a task card component.

    Usage: {% task_card task %}
    """
    return {'task': task}


@register.inclusion_tag('tasks/_task_stats.html')
def task_stats():
    """
    Render task statistics.

    Usage: {% task_stats %}
    """
    return {
        'total': Task.objects.count(),
        'completed': Task.objects.filter(status=Status.COMPLETED).count(),
        'pending': Task.objects.filter(status=Status.PENDING).count(),
        'in_progress': Task.objects.filter(status=Status.IN_PROGRESS).count(),
    }


# ============================================================
# ASSIGNMENT TAGS
# ============================================================

@register.simple_tag
def get_categories_with_counts():
    """
    Get all categories with their task counts.

    Usage: {% get_categories_with_counts as categories %}
    """
    from tasks.models import Category
    return Category.objects.annotate(task_count=Count('tasks'))