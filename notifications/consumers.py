"""
WebSocket consumers for real-time notifications.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time notifications.
    """

    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        self.user = self.scope["user"]

        logger.info(f"Notification WebSocket connection attempt - User: {self.user}")

        if self.user.is_anonymous:
            # Reject connection for anonymous users
            logger.warning("Notification WebSocket rejected - Anonymous user")
            await self.close()
        else:
            # Create a unique group name for this user
            self.group_name = f"notifications_{self.user.id}"

            # Join the user's notification group
            await self.channel_layer.group_add(self.group_name, self.channel_name)

            await self.accept()

            logger.info(
                f"✓ Notification WebSocket connected - User: {self.user.username}, Group: {self.group_name}"
            )

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        logger.info(
            f"Notification WebSocket disconnected - User: {self.user.username if hasattr(self, 'user') else 'Unknown'}, Close code: {close_code}"
        )

        if hasattr(self, "group_name"):
            # Leave the notification group
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.debug(f"Removed from notification group {self.group_name}")

    async def receive(self, text_data):
        """
        Called when we receive a message from the WebSocket.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get("type", "")

            logger.debug(
                f"Notification WebSocket message - User: {self.user.username}, Type: {message_type}"
            )

            if message_type == "ping":
                # Respond to ping with pong
                await self.send(
                    text_data=json.dumps(
                        {"type": "pong", "timestamp": data.get("timestamp")}
                    )
                )
                logger.debug(f"Pong sent to {self.user.username}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received from {self.user.username}: {e}")

    async def notification_message(self, event):
        """
        Called when a notification message is sent to the group.
        """
        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": "notification",
                    "notification": event["notification"],
                }
            )
        )
        logger.info(
            f"Notification sent to {self.user.username} - Type: {event['notification'].get('type', 'N/A')}"
        )
