from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import send_test_notification
from .views import save_fcm_token, update_notification_preferences
from .views import *

router = DefaultRouter()
router.register(r'notices', notice_view_set, basename='notice')
router.register(r'competitions', competition_view_set, basename='competition')
router.register(r'surveys', survey_view_set, basename='survey')
router.register(r'fests', fest_view_set, basename='fest')
router.register(r'seminars', seminar_view_set, basename='seminar')
router.register(r'student-initiatives', student_initiative_view_set, basename='student-initiative')
router.register(r'alumni', alumni_view_set, basename='alumni')

urlpatterns = [  
    path('create-user', view=create_user, name='create-user'),
    path('login/', view=login_page, name='login'),
    path('logout/', view=logout_user, name='logout'),
    path('', view=home, name="home"),
    path('create-notice/', view=create_notice, name="create-notice"),
    path('update-notice/<str:pk>', view=update_notice, name="update-notice"),
    path('delete-notice/<str:pk>', view=delete_notice, name="delete-notice"),
    path('create-competition/', view=create_competition, name="create-competition"),
    path('update-competition/<str:pk>', view=update_competition, name="update-competition"),
    path('delete-competition/<str:pk>', view=delete_competition, name="delete-competition"),
    path('create-seminar/', view=create_seminar, name="create-seminar"),
    path('update-seminar/<str:pk>', view=update_seminar, name="update-seminar"),
    path('delete-seminar/<str:pk>', view=delete_seminar, name="delete-seminar"),
    path('create-fest/', view=create_fest, name="create-fest"),
    path('update-fest/<str:pk>', view=update_fest, name="update-fest"),
    path('delete-fest/<str:pk>', view=delete_fest, name="delete-fest"),
    path('create-survey/', view=create_survey, name="create-survey"),
    path('update-survey/<str:pk>', view=update_survey, name="update-survey"),
    path('delete-survey/<str:pk>', view=delete_survey, name="delete-survey"),
    path('create-student-initiative/', view=create_studentinit, name="create-student-initiative"),
    path('update-student-initiative/<str:pk>', view=update_studentinit, name="update-student-initiative"),
    path('delete-student-initiative/<str:pk>', view=delete_studentinit, name="delete-student-initiative"),
    path('create-alumni/', view=create_alum, name="create-alumni"),
    path('update-alumni/<str:pk>', view=update_alum, name="update-alumni"),
    path('delete-alumni/<str:pk>', view=delete_alum, name="delete-alumni"),
    path('all-logs/', view=view_all_logs, name="all-logs"),
    path('privacy-policy/', view=privacy_policy_url, name="privacy-policy-url"),
    path('api/notification-preferences/', update_notification_preferences, name='notification-preferences'),
    path('api/save-fcm-token/', save_fcm_token, name='save-fcm-token'),
    path('send-test-notification/', send_test_notification),
    path('send-test-notification/', send_test_notification, name='send-test-notification'),
]

urlpatterns += router.urls
