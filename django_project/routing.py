"""
WebSocket URL routing for the django_project.
"""

from django.urls import path
from notifications import consumers as notification_consumers
from assessment import consumers as assessment_consumers

websocket_urlpatterns = [
    path("ws/notifications/", notification_consumers.NotificationConsumer.as_asgi()),
    path(
        "ws/assessment/<uuid:assessment_id>/",
        assessment_consumers.AssessmentConsumer.as_asgi(),
    ),
]
