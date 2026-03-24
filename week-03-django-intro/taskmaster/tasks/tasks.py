from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from .models import Task, Status


@shared_task
def send_task_reminder(task_id: int) -> str:
    """Send email reminder for a task."""
    try:
        task = Task.objects.get(pk=task_id)
        send_mail(
            subject=f'Reminder: {task.title}',
            message=f'Your task "{task.title}" is due on {task.due_date}',
            from_email='noreply@taskmaster.com',
            recipient_list=[task.owner.email],
        )
        return f'Reminder sent for task {task_id}'
    except Task.DoesNotExist:
        return f'Task {task_id} not found'


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def process_import(self, file_path: str) -> dict:
    """Process file import with retry on failure."""
    try:
        # Process file...
        return {'status': 'success', 'records': 100}
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def cleanup_old_tasks() -> int:
    """Delete completed tasks older than 90 days."""
    cutoff = timezone.now() - timedelta(days=90)
    deleted, _ = Task.objects.filter(
        status=Status.COMPLETED,
        completed_at__lt=cutoff
    ).delete()
    return deleted


@shared_task
def generate_report(user_id: int) -> str:
    """Generate user report (long-running task)."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    user = User.objects.get(pk=user_id)
    tasks = Task.objects.filter(owner=user)

    # Generate report...
    report_url = '/reports/user_report.pdf'

    # Notify user
    send_mail(
        subject='Your report is ready',
        message=f'Download your report: {report_url}',
        from_email='noreply@taskmaster.com',
        recipient_list=[user.email],
    )

    return report_url