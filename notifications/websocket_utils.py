"""
Utility functions for sending WebSocket notifications.
"""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_notification_to_user(user_id, notification_data):
    """
    Send a notification to a specific user via WebSocket.

    Args:
        user_id: The ID of the user to send the notification to
        notification_data: Dictionary containing notification data
            Example: {
                "title": "Assessment Complete",
                "message": "Your assessment for example.com is ready",
                "type": "success",  # success, info, warning, error
                "url": "/assessment/results/123/",
                "timestamp": "2026-01-18T15:00:00Z"
            }
    """
    channel_layer = get_channel_layer()
    group_name = f"notifications_{user_id}"

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "notification_message",
            "notification": notification_data,
        },
    )
