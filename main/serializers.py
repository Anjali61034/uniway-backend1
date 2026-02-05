from rest_framework import serializers
from .models import *

class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        exclude = ['removal_date', 'created_by', 'date_created']

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        exclude = ['date_created']

class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        exclude = ['date_created']

class FestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fest
        exclude = ['date_created']

class SeminarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seminar
        exclude = ['date_created']
        # ✅ FIX ADDED HERE
        # This tells the API validation that 'link' is optional
        extra_kwargs = {
            'link': {'required': False, 'allow_null': True, 'allow_blank': True}
        }

class StudentInitiativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInitiative
        exclude = ['date_created']

class AlumniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumni
        exclude = ['date_created', 'created_by']