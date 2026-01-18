import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Notification

logger = logging.getLogger(__name__)


@login_required
def notifications(request):
    """Notifications page"""
    user_notifications = Notification.objects.filter(user=request.user)
    unread_count = user_notifications.filter(is_read=False).count()
    
    # Mark as read if requested
    if request.GET.get('mark_read'):
        notification_id = request.GET.get('mark_read')
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            logger.info(f"User {request.user.username} marked notification {notification_id} as read")
            return redirect('notifications')
        except Notification.DoesNotExist:
            pass
    
    # Mark all as read
    if request.GET.get('mark_all_read'):
        user_notifications.filter(is_read=False).update(is_read=True)
        logger.info(f"User {request.user.username} marked all notifications as read")
        messages.success(request, "All notifications marked as read")
        return redirect('notifications')
    
    logger.info(f"User {request.user.username} accessed notifications page")
    template_path = "notifications/notifications.html"
    context = {
        'notifications': user_notifications,
        'unread_count': unread_count,
    }
    return render(request, template_path, context)
