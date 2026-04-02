from .models import Notification

def notification_count(request):
    """Inject unread notification count into every template context."""
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return {'unread_notification_count': count}
    return {'unread_notification_count': 0}
