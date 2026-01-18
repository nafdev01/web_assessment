"""Utility functions for notifications app"""
from .models import Notification


def create_notification(user, title, message, notification_type='info'):
    """
    Helper function to create notifications
    
    Args:
        user: Client instance
        title: Notification title
        message: Notification message
        notification_type: One of 'info', 'success', 'warning', 'error'
    
    Returns:
        Notification instance
    """
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type
    )


def notify_assessment_complete(user, target_url, vulnerabilities_count):
    """Create notification when assessment completes"""
    if vulnerabilities_count == 0:
        return create_notification(
            user=user,
            title='SCAN_COMPLETED',
            message=f'Vulnerability scan for target {target_url} completed. No vulnerabilities detected.',
            notification_type='success'
        )
    elif vulnerabilities_count < 5:
        return create_notification(
            user=user,
            title='SCAN_COMPLETED',
            message=f'Vulnerability scan for target {target_url} completed. {vulnerabilities_count} vulnerabilities detected.',
            notification_type='info'
        )
    else:
        return create_notification(
            user=user,
            title='HIGH_VULNERABILITY_COUNT',
            message=f'Vulnerability scan for target {target_url} completed. {vulnerabilities_count} vulnerabilities detected. Review recommended.',
            notification_type='warning'
        )


def notify_critical_vulnerability(user, target_url, vulnerability_type):
    """Create notification for critical vulnerabilities"""
    return create_notification(
        user=user,
        title='CRITICAL_VULNERABILITY_DETECTED',
        message=f'Critical vulnerability detected on {target_url}: {vulnerability_type}. Immediate action required.',
        notification_type='error'
    )
