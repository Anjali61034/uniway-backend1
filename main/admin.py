from django.contrib import admin
from .models import *

# Regular models
admin.site.register(Notice)
admin.site.register(Competition)
admin.site.register(Survey)
admin.site.register(Fest)
admin.site.register(Seminar)
admin.site.register(StudentInitiative)
admin.site.register(Alumni)

# Notification-related models
admin.site.register(UserFCMToken)
admin.site.register(NotificationPreference)
admin.site.register(NotificationLog)

# Custom Token model (if you want it in admin)
admin.site.register(CustomToken)