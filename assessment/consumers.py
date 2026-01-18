"""
WebSocket consumers for real-time assessment updates.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import VulnAssessment

logger = logging.getLogger(__name__)


class AssessmentConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time assessment progress updates.
    """

    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        self.user = self.scope["user"]
        self.assessment_id = self.scope["url_route"]["kwargs"]["assessment_id"]

        logger.info(
            f"WebSocket connection attempt - User: {self.user}, Assessment: {self.assessment_id}"
        )

        if self.user.is_anonymous:
            # Reject connection for anonymous users
            logger.warning(
                f"WebSocket connection rejected - Anonymous user attempted to connect to assessment {self.assessment_id}"
            )
            await self.close()
            return

        # Verify user owns this assessment
        has_access = await self.check_assessment_access()
        if not has_access:
            logger.warning(
                f"WebSocket connection rejected - User {self.user.username} does not have access to assessment {self.assessment_id}"
            )
            await self.close()
            return

        # Create a unique group name for this assessment
        self.group_name = f"assessment_{self.assessment_id}"

        # Join the assessment group
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

        logger.info(
            f"✓ WebSocket connected successfully - User: {self.user.username}, Assessment: {self.assessment_id}, Group: {self.group_name}"
        )

        # Send initial status
        status = await self.get_assessment_status()
        await self.send(
            text_data=json.dumps(
                {
                    "type": "status",
                    "status": status,
                }
            )
        )
        logger.debug(
            f"Sent initial status to {self.user.username} for assessment {self.assessment_id}"
        )

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        logger.info(
            f"WebSocket disconnected - User: {self.user.username if hasattr(self, 'user') else 'Unknown'}, Assessment: {self.assessment_id if hasattr(self, 'assessment_id') else 'Unknown'}, Close code: {close_code}"
        )

        if hasattr(self, "group_name"):
            # Leave the assessment group
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.debug(f"Removed from group {self.group_name}")

    async def receive(self, text_data):
        """
        Called when we receive a message from the WebSocket.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get("type", "")

            logger.debug(
                f"WebSocket message received - User: {self.user.username}, Type: {message_type}"
            )

            if message_type == "ping":
                # Respond to ping with pong
                await self.send(
                    text_data=json.dumps(
                        {"type": "pong", "timestamp": data.get("timestamp")}
                    )
                )
                logger.debug(f"Pong sent to {self.user.username}")
            elif message_type == "request_status":
                # Send current status
                status = await self.get_assessment_status()
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "status",
                            "status": status,
                        }
                    )
                )
                logger.debug(f"Status update sent to {self.user.username}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received from {self.user.username}: {e}")

    async def assessment_update(self, event):
        """
        Called when an assessment update is sent to the group.
        """
        # Send update to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": "update",
                    "update": event["update"],
                }
            )
        )
        logger.debug(
            f"Assessment update sent - Line: {event['update'].get('line_number', 'N/A')}"
        )

    async def assessment_progress(self, event):
        """
        Called when assessment progress is updated.
        """
        # Send progress to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": "progress",
                    "progress": event["progress"],
                }
            )
        )
        logger.info(
            f"Progress update sent - Stage: {event['progress'].get('stage')}, Percentage: {event['progress'].get('percentage')}%"
        )

    async def assessment_complete(self, event):
        """
        Called when assessment is complete.
        """
        # Send completion message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": "complete",
                    "data": event["data"],
                }
            )
        )
        logger.info(
            f"✓ Assessment complete notification sent - Assessment: {self.assessment_id}, Vulnerabilities: {event['data'].get('vulnerabilities_count', 0)}"
        )

    @database_sync_to_async
    def check_assessment_access(self):
        """
        Check if the user has access to this assessment.
        """
        try:
            assessment = VulnAssessment.objects.get(id=self.assessment_id)
            has_access = assessment.client == self.user
            logger.debug(
                f"Access check - User: {self.user.username}, Assessment: {self.assessment_id}, Has access: {has_access}"
            )
            return has_access
        except VulnAssessment.DoesNotExist:
            logger.error(f"Assessment {self.assessment_id} does not exist")
            return False

    @database_sync_to_async
    def get_assessment_status(self):
        """
        Get the current status of the assessment.
        """
        try:
            assessment = VulnAssessment.objects.get(id=self.assessment_id)
            return {
                "assessment_id": str(assessment.id),
                "website": assessment.website,
                "ready": assessment.ready,
                "tested_on": (
                    assessment.tested_on.isoformat() if assessment.tested_on else None
                ),
            }
        except VulnAssessment.DoesNotExist:
            logger.error(
                f"Assessment {self.assessment_id} not found when getting status"
            )
            return None
