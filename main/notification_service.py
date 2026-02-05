import json
import logging
from typing import List
from django.conf import settings
from firebase_admin import messaging, credentials, initialize_app
from django.utils import timezone
import firebase_admin
import os
from pathlib import Path

logger = logging.getLogger('uniway-backend')

class FirebaseNotificationService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialize_firebase()
            self._initialized = True

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not firebase_admin._apps:
                # Path to your Firebase credentials JSON file
                cred_path = os.path.join(settings.BASE_DIR, 'firebase-credentials.json')
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    initialize_app(cred)
                    logger.info("Firebase Admin SDK initialized successfully")
                else:
                    logger.error("Firebase credentials file not found at: " + cred_path)
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")

    def get_notification_content(self, event_type: str, event_name: str):
        """Get notification title, body, and route based on event type"""
        content_map = {
            'competition': {
                'title': '🎉 New Competition Added!',
                'body': f'{event_name}',
                'route': '/updates'
            },
            'seminar': {
                'title': '📚 New Seminar Available!',
                'body': f'{event_name}',
                'route': '/seminars'
            },
            'fest': {
                'title': '🎊 New Fest Announced!',
                'body': f'{event_name}',
                'route': '/fests'
            },
            'survey': {
                'title': '📋 New Survey Available!',
                'body': f'{event_name}',
                'route': '/surveys'
            },
            'student_initiative': {
                'title': '🌟 New Student Initiative!',
                'body': f'{event_name}',
                'route': '/studentinitiatives'
            },
            'alumni': {
                'title': '🎓 New Alumni Featured!',
                'body': f'{event_name}',
                'route': '/alumnae'
            }
        }

        default = {'title': '📢 New Update!', 'body': event_name, 'route': '/home'}
        return content_map.get(event_type, default)

    def get_active_tokens_for_event_type(self, event_type: str):
        """Get FCM tokens for users who want notifications for this event type"""
        from .models import UserFCMToken, NotificationPreference

        try:
            # Get all active FCM tokens
            active_tokens = UserFCMToken.objects.filter(is_active=True)

            # Map event type to preference field
            preference_mapping = {
                'competition': 'competitions_enabled',
                'seminar': 'seminars_enabled',
                'fest': 'fests_enabled',
                'survey': 'surveys_enabled',
                'student_initiative': 'student_initiatives_enabled',
                'alumni': 'alumni_enabled'
            }

            preference_field = preference_mapping.get(event_type)

            if preference_field:
                # Get users who have enabled this notification type
                enabled_users = NotificationPreference.objects.filter(
                    **{preference_field: True}
                ).values_list('user_email', flat=True)

                if enabled_users:
                    tokens = active_tokens.filter(user_email__in=enabled_users)
                else:
                    # If no preferences set, send to all users
                    tokens = active_tokens
            else:
                tokens = active_tokens

            return list(tokens.values_list('fcm_token', flat=True))

        except Exception as e:
            logger.error(f"Error getting FCM tokens: {e}")
            return []

    def send_notification(self, event_type: str, event_name: str, event_id: int, sent_by=None):
        """Send push notification for new events"""
        from .models import NotificationLog

        try:
            # Get notification content
            content = self.get_notification_content(event_type, event_name)
            title = content['title']
            body = content['body']
            route = content['route']

            # Get active FCM tokens
            tokens = self.get_active_tokens_for_event_type(event_type)

            if not tokens:
                logger.warning(f"No FCM tokens found for {event_type} notifications")
                return False

            # Prepare the message
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data={
                    'event_type': event_type,
                    'event_id': str(event_id),
                    'route': route,
                    'created_at': timezone.now().isoformat(),
                },
                tokens=tokens,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='@mipmap/ic_launcher',
                        color='#0B5555',
                        sound='default',
                    )
                ),
                apns=messaging.APNSConfig(
                    headers={'apns-priority': '10'},
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            alert=messaging.ApsAlert(title=title, body=body),
                            badge=1,
                            sound='default'
                        )
                    )
                )
            )

            # Send the message
            response = messaging.send_each_for_multicast(message)

            # Log the notification
            NotificationLog.objects.create(
                title=title,
                body=body,
                event_type=event_type,
                event_id=event_id,
                recipients_count=len(tokens),
                success_count=response.success_count,
                failure_count=len(tokens) - response.success_count,
                sent_by=sent_by
            )

            logger.info(f"Notification sent: {response.success_count}/{len(tokens)} successful")

            # Handle failed tokens
            if response.failure_count > 0:
                failed_tokens = []
                for idx, resp in enumerate(response.responses):
                    if not resp.success:
                        failed_tokens.append(tokens[idx])

                # Deactivate failed tokens
                from .models import UserFCMToken
                UserFCMToken.objects.filter(fcm_token__in=failed_tokens).update(is_active=False)

            return response.success_count > 0

        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False

# Create a global instance
notification_service = FirebaseNotificationService()