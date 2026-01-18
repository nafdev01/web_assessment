"""
Utility functions for sending WebSocket messages.
"""

import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


def send_notification_to_user(user_id, notification_data):
    """
    Send a notification to a specific user via WebSocket.

    Args:
        user_id: The ID of the user to send the notification to
        notification_data: Dictionary containing notification data
    """
    try:
        channel_layer = get_channel_layer()
        group_name = f"notifications_{user_id}"

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "notification_message",
                "notification": notification_data,
            },
        )
        logger.debug(f"Notification sent to user {user_id}")
    except Exception as e:
        logger.error(f"Error sending notification to user {user_id}: {e}")


def send_assessment_update(assessment_id, update_data):
    """
    Send an assessment update via WebSocket.

    Args:
        assessment_id: The ID of the assessment
        update_data: Dictionary containing update information
    """
    try:
        channel_layer = get_channel_layer()
        group_name = f"assessment_{assessment_id}"

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "assessment_update",
                "update": update_data,
            },
        )
    except Exception as e:
        logger.error(f"Error sending assessment update for {assessment_id}: {e}")


def send_assessment_progress(assessment_id, progress_data):
    """
    Send assessment progress update via WebSocket.

    Args:
        assessment_id: The ID of the assessment
        progress_data: Dictionary containing progress information (e.g., percentage, stage, message)
    """
    try:
        channel_layer = get_channel_layer()
        group_name = f"assessment_{assessment_id}"

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "assessment_progress",
                "progress": progress_data,
            },
        )
        logger.debug(
            f"Progress update sent for {assessment_id}: {progress_data.get('percentage')}%"
        )
    except Exception as e:
        logger.error(f"Error sending progress update for {assessment_id}: {e}")


def send_assessment_complete(assessment_id, completion_data):
    """
    Send assessment completion notification via WebSocket.

    Args:
        assessment_id: The ID of the assessment
        completion_data: Dictionary containing completion information
    """
    try:
        channel_layer = get_channel_layer()
        group_name = f"assessment_{assessment_id}"

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "assessment_complete",
                "data": completion_data,
            },
        )
        logger.info(f"Completion notification sent for {assessment_id}")
    except Exception as e:
        logger.error(f"Error sending completion notification for {assessment_id}: {e}")
