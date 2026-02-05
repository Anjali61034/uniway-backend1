from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.authtoken.models import Token
import logging

# Import signals at the bottom to avoid circular imports
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger('uniway-backend')

class CustomToken(Token):
    READ_ONLY_SCOPE = 'read_only'
    scope = models.CharField(max_length=20, default=READ_ONLY_SCOPE)

class Notice(models.Model):
    heading = models.CharField(max_length=100, null=True, blank=True)
    notice_img = models.FileField(upload_to="notices", default="default-poster.png", null=True, blank=True)
    removal_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.heading

class Competition(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=300, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    link = models.URLField(max_length=200, null=True, blank=True) 
    poster = models.ImageField(upload_to="updates", default="default-poster.png", null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.department} - {self.name}"

class Survey(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=300, null=True, blank=True)
    link = models.URLField(max_length=200, null=True, blank=True) 
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.department} - {self.name}"

class Fest(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=300, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    poster = models.ImageField(upload_to="fests", default="default-poster.png", null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.department}"

class Seminar(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    
    # CHANGED: Removed default="", so it saves as NULL in DB if empty
    # CHANGED: Increased max_length to 200 for safety
    link = models.URLField(max_length=200, null=True, blank=True) 
    
    poster = models.ImageField(upload_to="seminars", default="default-poster.png", null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.department} - {self.name}"

class StudentInitiative(models.Model):
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, null=True, blank=True)
    student_name = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=300, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.student_name})"

class Alumni(models.Model):
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=50, null=True, blank=True)
    batch = models.IntegerField(null=True, blank=True)
    information = models.CharField(max_length=300, null=True, blank=True)
    linkedin_link = models.URLField(default="", max_length=100, null=True, blank=True)
    picture = models.ImageField(upload_to="alum", default="default-poster.png", null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.department})"

class UserFCMToken(models.Model):
    """Store FCM tokens for push notifications"""
    user_email = models.EmailField(unique=True)
    fcm_token = models.TextField()
    platform = models.CharField(max_length=20, choices=[
        ('android', 'Android'),
        ('ios', 'iOS'),
    ], default='android')
    app_version = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_email} - {self.platform}"

class NotificationPreference(models.Model):
    """User notification preferences"""
    user_email = models.EmailField(unique=True)
    competitions_enabled = models.BooleanField(default=True)
    seminars_enabled = models.BooleanField(default=True)
    fests_enabled = models.BooleanField(default=True)
    surveys_enabled = models.BooleanField(default=True)
    student_initiatives_enabled = models.BooleanField(default=True)
    alumni_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user_email}"

class NotificationLog(models.Model):
    """Log sent notifications for tracking"""
    title = models.CharField(max_length=200)
    body = models.TextField()
    event_type = models.CharField(max_length=50)
    event_id = models.IntegerField()
    recipients_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.title} - {self.event_type}"


# Auto-send notifications when events are created via Django admin
@receiver(post_save, sender=Notice)
def notice_created_signal(sender, instance, created, **kwargs):
    if created:  # Only when new notice is created
        logger.info(f"Signal: New notice created: {instance.heading}")
        try:
            from .notification_service import notification_service
            notification_service.send_notification(
                event_type='notice',
                event_name=instance.heading,
                event_id=instance.id,
                sent_by='admin_signal'
            )
        except Exception as e:
            logger.error(f"Error sending notice notification: {e}")

@receiver(post_save, sender=Competition)
def competition_created_signal(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Signal: New competition created: {instance.name}")
        try:
            from .notification_service import notification_service
            notification_service.send_notification(
                event_type='competition',
                event_name=instance.name,
                event_id=instance.id,
                sent_by='admin_signal'
            )
        except Exception as e:
            logger.error(f"Error sending competition notification: {e}")

@receiver(post_save, sender=Seminar)
def seminar_created_signal(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Signal: New seminar created: {instance.name}")
        try:
            from .notification_service import notification_service
            notification_service.send_notification(
                event_type='seminar',
                event_name=instance.name,
                event_id=instance.id,
                sent_by='admin_signal'
            )
        except Exception as e:
            logger.error(f"Error sending seminar notification: {e}")

@receiver(post_save, sender=Fest)
def fest_created_signal(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Signal: New fest created: {instance.name}")
        try:
            from .notification_service import notification_service
            notification_service.send_notification(
                event_type='fest',
                event_name=instance.name,
                event_id=instance.id,
                sent_by='admin_signal'
            )
        except Exception as e:
            logger.error(f"Error sending fest notification: {e}")

@receiver(post_save, sender=Survey)
def survey_created_signal(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Signal: New survey created: {instance.name}")
        try:
            from .notification_service import notification_service
            notification_service.send_notification(
                event_type='survey',
                event_name=instance.name,
                event_id=instance.id,
                sent_by='admin_signal'
            )
        except Exception as e:
            logger.error(f"Error sending survey notification: {e}")

@receiver(post_save, sender=StudentInitiative)
def student_initiative_created_signal(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Signal: New student initiative created: {instance.name}")
        try:
            from .notification_service import notification_service
            notification_service.send_notification(
                event_type='student_initiative',
                event_name=instance.name,
                event_id=instance.id,
                sent_by='admin_signal'
            )
        except Exception as e:
            logger.error(f"Error sending student initiative notification: {e}")

@receiver(post_save, sender=Alumni)
def alumni_created_signal(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Signal: New alumni featured: {instance.name}")
        try:
            from .notification_service import notification_service
            notification_service.send_notification(
                event_type='alumni',
                event_name=instance.name,
                event_id=instance.id,
                sent_by='admin_signal'
            )
        except Exception as e:
            logger.error(f"Error sending alumni notification: {e}")

from django.contrib.auth.models import User

class FCMDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.user.username
