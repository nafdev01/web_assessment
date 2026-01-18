from django.core.management.base import BaseCommand
from accounts.models import Client
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Create sample notifications for testing'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to create notifications for')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = Client.objects.get(username=username)
        except Client.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))
            return

        # Create sample notifications
        notifications = [
            {
                'title': 'SYSTEM_INITIALIZED',
                'message': 'Web Vulnerability Assessment Tool has been successfully initialized. All systems operational.',
                'notification_type': 'success',
            },
            {
                'title': 'SCAN_COMPLETED',
                'message': 'Vulnerability scan for target https://example.com completed. 3 vulnerabilities detected.',
                'notification_type': 'info',
            },
            {
                'title': 'HIGH_SEVERITY_ALERT',
                'message': 'Critical vulnerability detected: SQL Injection vulnerability found in login form. Immediate action required.',
                'notification_type': 'error',
            },
            {
                'title': 'SECURITY_UPDATE',
                'message': 'New security patches available. System update recommended within 24 hours.',
                'notification_type': 'warning',
            },
            {
                'title': 'ASSESSMENT_READY',
                'message': 'Your scheduled assessment report is ready for review. Access it from the History section.',
                'notification_type': 'success',
            },
        ]

        created_count = 0
        for notif_data in notifications:
            Notification.objects.create(
                user=user,
                **notif_data
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} notifications for user "{username}"')
        )
