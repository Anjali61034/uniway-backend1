from django.shortcuts import render, redirect
from django.contrib import messages
import os
from django.conf import settings


from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import FCMDevice

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from .models import UserFCMToken, NotificationPreference
from .notification_service import notification_service

from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets

from .models import *
from .forms import *
from.helpers import *
from .decorators import *
from .serializers import *

import fitz
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile

import logging
logger = logging.getLogger('uniway-backend')

@admin_only
def create_user(request):
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = user.username
            group = Group.objects.get(name='dept_head')
            user.groups.add(group)
            logger.info(f'User - {username}, created.')
            return redirect('/login/')
        else:
            logger.error("Unable to create user.")
    context = {'form': form, 
               'user_form': True}
    return render(request, 'main/form.html', context)

@unauthenticated_user
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            logger.info(f'{user} logged in.')
            return redirect('home')
        else: 
            logger.error(f'{user} tried to log in but failed.')
            messages.error(request, "Invalid username or password.")
            return render(request, 'main/login.html')
    return render(request, 'main/login.html')

def logout_user(request):
    user = request.user
    logout(request)
    logger.info(f'{user} logged out.')
    return redirect('login')

@login_required(login_url='login')
def home(request):
    if request.user.is_staff:
        notices = Notice.objects.all().order_by('-date_created')
        competitions = Competition.objects.all().order_by('-date_created')
        seminars = Seminar.objects.all().order_by('-date_created')
        fests = Fest.objects.all().order_by('-date_created')
        surveys = Survey.objects.all().order_by('-date_created')
        student_initiatives = StudentInitiative.objects.all().order_by('-date_created')
        alumnae = Alumni.objects.all().order_by('-date_created')

        log_file_path = os.path.join(settings.BASE_DIR, 'info.log')
        with open(log_file_path, 'r') as log_file:
            log_entries = log_file.readlines()
            log_entries = log_entries[-10:]
        context = {
            'notices': notices,
            'competitions': competitions,
            'seminars': seminars,
            'fests': fests,
            'surveys': surveys,
            'student_initiatives':  student_initiatives,
            'alumnae': alumnae,
            'log_entries': log_entries
        }
        return render(request, 'main/admin-home.html', context)
    user = str(request.user)
    user = convert_to_dept_name(user).title()
    competitions = Competition.objects.filter(created_by=request.user).order_by('-date_created')
    notices = Notice.objects.filter(created_by=request.user).order_by('-date_created')
    seminars = Seminar.objects.filter(created_by=request.user).order_by('-date_created')
    fests = Fest.objects.filter(created_by=request.user).order_by('-date_created')
    surveys = Survey.objects.filter(created_by=request.user).order_by('-date_created')
    student_initiatives = StudentInitiative.objects.filter(created_by=request.user).order_by('-date_created')
    alumnae = Alumni.objects.filter(created_by=request.user).order_by('-date_created')
    context = {
        'notices': notices,
        'competitions': competitions,
        'seminars': seminars,
        'fests': fests,
        'surveys': surveys,
        'student_initiatives':  student_initiatives,
        'alumnae': alumnae
    }
    return render(request, 'main/home.html', context)

@admin_only
def view_all_logs(request):
    log_file_path = os.path.join(settings.BASE_DIR, 'info.log')
    with open(log_file_path, 'r') as log_file:
        log_entries = log_file.readlines()
    context = {'log_entries': log_entries}
    return render(request, 'main/logs.html', context)

@login_required(login_url='login')
def create_notice(request):
    form = NoticeForm()
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES)
        if form.is_valid():
            heading = form.cleaned_data.get('heading')
            notice_img = form.cleaned_data.get('notice_img')
            removal_date = form.cleaned_data.get('removal_date')
            if notice_img.content_type == 'application/pdf':
                pdf_document = fitz.open(stream=notice_img.read(), filetype='pdf')
                pdf_page = pdf_document.load_page(0)  # Load the first page
                pdf_image = pdf_page.get_pixmap()
                image = Image.frombytes("RGB", [pdf_image.width, pdf_image.height], pdf_image.samples)
                png_name = f'{os.path.splitext(notice_img.name)[0]}.png'
                image_io = BytesIO()
                image.save(image_io, format='PNG')
                image_io.seek(0)
                notice_img = ContentFile(image_io.read(), name=png_name)
            notice = Notice.objects.create(
                heading=heading,
                notice_img=notice_img,
                removal_date=removal_date,
                created_by=request.user,
                )
            notice.save()
            logger.info(f'{request.user} created an entry - {heading}, in Notices.')
            return redirect('/')
        else:
            logger.warning(f'{request.user} was unable to create an entry in Notices.')
    context = {'form': form,
               'notice_form': True}
    return render(request, 'main/form.html', context)

@login_required(login_url='login')
def update_notice(request, pk):
    notice = Notice.objects.get(id=pk)
    form = NoticeForm(instance=notice)
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES, instance=notice)
        if form.is_valid():
            notice_img = form.cleaned_data.get('notice_img')
            if notice_img and notice_img.content_type == 'application/pdf':
                pdf_document = fitz.open(stream=notice_img.read(), filetype='pdf')
                pdf_page = pdf_document.load_page(0)  # Load the first page
                pdf_image = pdf_page.get_pixmap()
                image = Image.frombytes("RGB", [pdf_image.width, pdf_image.height], pdf_image.samples)
                png_name = f'{os.path.splitext(notice_img.name)[0]}.png'
                image_io = BytesIO()
                image.save(image_io, format='PNG')
                image_io.seek(0)
                notice_img = ContentFile(image_io.read(), name=png_name)
                notice.notice_img = notice_img
            form.save()
            heading = form.cleaned_data.get('heading')
            user = str(request.user)
            logger.info(f'{user} updated an entry - {heading}, in Notices.')
            return redirect('home')
        else:
            logger.warning(f'{request.user} was unable to update an entry in Notices.')
    context = {'form': form,
               'notice': notice,
               'notice_form': True,
               'update': True}
    return render(request, 'main/form.html', context)

@login_required(login_url='login')
def delete_notice(request, pk):
    notice = Notice.objects.get(id=pk)
    if request.method == 'POST':
        heading = notice.heading
        notice.delete()
        user = str(request.user)
        user = convert_to_dept_name(user).title()
        dept = f"Department of {user}"
        logger.warning(f'{dept} deleted an entry - {heading}, from notices.')
        return redirect('home')
    context = {'instance': notice}
    return render(request, 'main/delete.html', context)

@login_required(login_url='login')
def create_competition(request):
    form = CompetitionForm()
    if request.method == 'POST':
        form = CompetitionForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            desc = form.cleaned_data.get('description')
            date = form.cleaned_data.get('date')
            link = form.cleaned_data.get('link')
            poster = form.cleaned_data.get('poster')
            department = form.cleaned_data.get('department')
            if not department:
                user = str(request.user)
                user = convert_to_dept_name(user).title()
                dept = f"Department of {user}"
            else:
                dept = f"Department of {department.title()}"
            competition = Competition.objects.create(
                name=name,
                description=desc,
                department=dept,
                date=date,
                link=link,
                poster=poster,
                created_by=request.user
                )
            competition.save()
            logger.info(f'{request.user} created an entry - {name}, in Events and competitions.')
            return redirect('/')
        else:
            logger.warning(f'{request.user} was unable to create an entry in Events and competitions.')
    context = {'form': form,
               'competition_form': True}
    return render(request, 'main/form.html', context)

@login_required(login_url='login')
def update_competition(request, pk):
    competition = Competition.objects.get(id=pk)
    form = CompetitionForm(instance=competition)
    if request.method == 'POST':
        form = CompetitionForm(request.POST, request.FILES, instance=competition)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            user = str(request.user)
            user = convert_to_dept_name(user).title()
            dept = f"Department of {user}"
            logger.info(f'{dept} updated an entry - {name}, in Events and Competitions.')
            return redirect('home')
        else:
            logger.warning(f'{request.user} was unable to update an entry in Events and Competitions.')
    context = {'form': form,
               'competition': competition,
               'competition_form': True,
               'update': True}
    return render(request, 'main/form.html', context)

@login_required(login_url='login')
def delete_competition(request, pk):
    competition = Competition.objects.get(id=pk)
    if request.method == 'POST':
        competition.delete()
        name = competition.name
        user = str(request.user)
        user = convert_to_dept_name(user).title()
        dept = f"Department of {user}"
        logger.warning(f'{dept} deleted an entry - {name}, from Events and Competitions.')
        return redirect('home')
    context = {'instance': competition}
    return render(request, 'main/delete.html', context)

@login_required(login_url='login')
def create_seminar(request):
    form = SeminarForm()

    if request.method == 'POST':
        form = SeminarForm(request.POST, request.FILES)

        if form.is_valid():
            name = form.cleaned_data.get('name')
            date = form.cleaned_data.get('date')
            link = form.cleaned_data.get('link')
            poster = form.cleaned_data.get('poster')
            department = form.cleaned_data.get('department')

            # Build department string
            if not department:
                user = str(request.user)
                user = convert_to_dept_name(user).title()
                dept = f"Department of {user}"
            else:
                dept = f"Department of {department.title()}"

            # ✅ SAFETY CHECK (prevents varchar(50/100) crash)
            if len(dept) > 100:
                form.add_error('department', 'Department name is too long')
                return render(request, 'main/form.html', {
                    'form': form,
                    'seminar_form': True
                })

            # Create seminar (create() already saves)
            seminar = Seminar.objects.create(
                name=name,
                date=date,
                department=dept,
                link=link,
                poster=poster,
                created_by=request.user
            )

            # Send notification
            notification_service.send_notification(
                'seminar', name, seminar.id, request.user
            )

            logger.info(f'{request.user} created an entry - {name}, in Seminars.')
            return redirect('/')

        else:
            logger.warning(f'{request.user} was unable to create an entry in Seminars.')

    context = {
        'form': form,
        'seminar_form': True
    }
    return render(request, 'main/form.html', context)

@login_required(login_url='login')
def update_seminar(request, pk):
    seminar = Seminar.objects.get(id=pk)
    form = SeminarForm(instance=seminar)
    if request.method == 'POST':
        form = SeminarForm(request.POST, request.FILES, instance=seminar)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            user = str(request.user)
            user = convert_to_dept_name(user).title()
            dept = f"Department of {user}"
            logger.info(f'{dept} updated an entry - {name}, in Seminars.')
            return redirect('home')
        else:
            logger.warning(f'{request.user} was unable to update an entry in Seminars.')
    context = {'form': form,
               'seminar': seminar,
               'seminar_form': True,
               'update': True}
    return render(request, 'main/form.html', context)

@login_required(login_url='login')
def delete_seminar(request, pk):
    seminar = Seminar.objects.get(id=pk)
    if request.method == 'POST':
        seminar.delete()
        name = seminar.name
        user = str(request.user)
        user = convert_to_dept_name(user).title()
        dept = f"Department of {user}"
        logger.warning(f'{dept} deleted an entry - {name}, from Seminars.')
        return redirect('home')
    context = {'instance': seminar}
    return render(request, 'main/delete.html', context)

@login_required(login_url='login')
def create_fest(request):
    form = FestForm()
    if request.method == 'POST':
        form = FestForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            desc = form.cleaned_data.get('description')
            date = form.cleaned_data.get('date')
            poster = form.cleaned_data.get('poster')
            department = form.cleaned_data.get('department')
            if not department:
                user = str(request.user)
                user = convert_to_dept_name(user).title()
                dept = f"Department of {user}"
            else:
                dept = f"Department of {department.title()}"
            fest = Fest.objects.create(
                name=name,
                description=desc,
                department=dept,
                date=date,
                poster=poster,
                created_by=request.user
                )
            fest.save()
            logger.info(f'{request.user} created an entry - {name}, in Fests.')
            return redirect('/')
        else:
            logger.warning(f'{request.user} was unable to create an entry in Fests.')
    context = {'form': form,
               'fest_form': True}
    return render(request, 'main/form.html', context)

@login_required(login_url='login')
def update_fest(request, pk):
    fest = Fest.objects.get(id=pk)
    form = FestForm(instance=fest)
    if request.method == 'POST':
        form = FestForm(request.POST, request.FILES, instance=fest)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            user = str(request.user)
            user = convert_to_dept_name(user).title()
            dept = f"Department of {user}"
            logger.info(f'{dept} updated an entry - {name}, in Fests.')
            return redirect('home')
        else:
            logger.warning(f'{request.user} was unable to update an entry in Fests.')
    context = {'form': form,
               'fest': fest,
               'fest_form': True,
               'update': True}
    return render(request, 'main/form.html', context)

@login_required(login_url='login')
def delete_fest(request, pk):
    fest = Fest.objects.get(id=pk)
    if request.method == 'POST':
        fest.delete()
        name = fest.name
        user = str(request.user)
        user = convert_to_dept_name(user).title()
        dept = f"Department of {user}"
        logger.warning(f'{dept} deleted an entry - {name}, from Fests.')
        return redirect('home')
    context = {'instance': fest}
    return render(request, 'main/delete.html', context)

@login_required(login_url='login')
def create_survey(request):
    form = SurveyForm()
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            desc = form.cleaned_data.get('description')
            link = form.cleaned_data.get('link')
            department = form.cleaned_data.get('department')
            if not department:
                user = str(request.user)
                user = convert_to_dept_name(user).title()
                dept = f"Department of {user}"
            else:
                dept = f"Department of {department.title()}"
            survey = Survey.objects.create(
                name=name,
                description=desc,
                department=dept,
                link=link,
                created_by=request.user
                )
            survey.save()
            logger.info(f'{request.user} created an entry - {name}, in Surveys.')
            return redirect('/')
        else:
            logger.warning(f'{request.user} was unable to create an entry in Surveys.')
    context = {'form': form,
               'survey_form': True}
    return render(request, 'main/form.html', context)

@login_required(login_url='login')
def update_survey(request, pk):
    survey = Survey.objects.get(id=pk)
    form = SurveyForm(instance=survey)
    if request.method == 'POST':
        form = SurveyForm(request.POST, instance=survey)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            user = str(request.user)
            user = convert_to_dept_name(user).title()
            dept = f"Department of {user}"
            logger.info(f'{dept} updated an entry - {name}, in Surveys.')
            return redirect('home')
        else:
            logger.warning(f'{request.user} was unable to update an entry in Surveys.')
    context = {'form': form,
               'survey': survey,
               'survey_form': True,
               'update': True}
    return render(request, 'main/form.html', context)

@login_required(login_url='login')
def delete_survey(request, pk):
    survey = Survey.objects.get(id=pk)
    if request.method == 'POST':
        survey.delete()
        name = survey.name
        user = str(request.user)
        user = convert_to_dept_name(user).title()
        dept = f"Department of {user}"
        logger.warning(f'{dept} deleted an entry - {name}, from Surveys.')
        return redirect('home')
    context = {'instance': survey}
    return render(request, 'main/delete.html', context)

@login_required(login_url='login')
def create_studentinit(request):
    form = StudentInitiativeForm()
    if request.method == 'POST':
        form = StudentInitiativeForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data.get('name')
            student_name = form.cleaned_data.get('student_name')
            desc = form.cleaned_data.get('description')
            user_name = convert_to_dept_name(str(user)).title()
            dept = f"Department of {user_name}"
            student_initiative = StudentInitiative.objects.create(
                created_by=user,
                name=name,
                student_name=student_name,
                description=desc,
                )
            student_initiative.save()
            logger.info(f'{request.user} created an entry - {name}, in Student Initiatives.')
            return redirect('/')
        else:
            logger.warning(f'{request.user} was unable to create an entry in Student Initiatives.')
    context = {'form': form,
               'student_initiative_form': True}
    return render(request, 'main/form.html', context)

@login_required(login_url='login')
def update_studentinit(request, pk):
    student_initiative = StudentInitiative.objects.get(id=pk)
    form = StudentInitiativeForm(instance=student_initiative)
    if request.method == 'POST':
        form = StudentInitiativeForm(request.POST, instance=student_initiative)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            user = str(request.user)
            user = convert_to_dept_name(user).title()
            dept = f"Department of {user}"
            logger.info(f'{dept} updated an entry - {name}, in Student Initiatives.')
            return redirect('home')
        else:
            logger.warning(f'{request.user} was unable to update an entry in Student Initiatives.')
    context = {'form': form,
               'student_initiative': student_initiative,
               'student_initiative_form': True,
               'update': True}
    return render(request, 'main/form.html', context)

@login_required(login_url='login')
def delete_studentinit(request, pk):
    student_initiative = StudentInitiative.objects.get(id=pk)
    if request.method == 'POST':
        student_initiative.delete()
        name = student_initiative.name
        user = str(request.user)
        user = convert_to_dept_name(user).title()
        dept = f"Department of {user}"
        logger.warning(f'{dept} deleted an entry - {name}, from Student Initiatives.')
        return redirect('home')
    context = {'instance': student_initiative}
    return render(request, 'main/delete.html', context)

@login_required(login_url='login')
def create_alum(request):
    form = AlumniForm()
    if request.method == 'POST':
        form = AlumniForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            batch = form.cleaned_data.get('batch')
            info = form.cleaned_data.get('information')
            link = form.cleaned_data.get('linkedin_link')
            picture = form.cleaned_data.get('picture')
            department = form.cleaned_data.get('department')
            user_object = request.user
            user = str(request.user)
            user = convert_to_dept_name(user).title()
            if not department:
                dept = f"Department of {user}"
            else:
                dept = f"Department of {department.title()}"
            alumni = Alumni.objects.create(
                created_by=user_object,
                name=name,
                department=dept,
                batch=batch,
                information=info,
		        linkedin_link=link,
                picture=picture
                )
            alumni.save()
            logger.info(f'{request.user} created an entry - {name} of batch {batch} in Alumni.')
            return redirect('/')
        else:
            logger.warning(f'{request.user} was unable to create an entry in Alumni.')
    context = {'form': form,
               'alum_form': True}
    return render(request, 'main/form.html', context)

@login_required(login_url='login')
def update_alum(request, pk):
    alum = Alumni.objects.get(id=pk)
    form = AlumniForm(instance=alum)
    if request.method == 'POST':
        form = AlumniForm(request.POST, request.FILES, instance=alum)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            user = str(request.user)
            user = convert_to_dept_name(user).title()
            dept = f"Department of {user}"
            logger.info(f'{dept} updated an entry - {name}, in Alumni.')
            return redirect('home')
        else:
            logger.warning(f'{request.user} was unable to update an entry in Alumni.')
    context = {'form': form,
               'alumni': alum,
               'alum_form': True,
               'update': True}
    return render(request, 'main/form.html', context)

@login_required(login_url='login')
def delete_alum(request, pk):
    alum = Alumni.objects.get(id=pk)
    if request.method == 'POST':
        alum.delete()
        name = alum.name
        user = str(request.user)
        user = convert_to_dept_name(user).title()
        dept = f"Department of {user}"
        logger.warning(f'{dept} deleted an entry - {name}, from Alumni.')
        return redirect('home')
    context = {'instance': alum}
    return render(request, 'main/delete.html', context)

class notice_view_set(viewsets.ModelViewSet):
    current_date = timezone.now().date()
    queryset = Notice.objects.filter(removal_date__gt=current_date).order_by('-date_created')
    serializer_class = NoticeSerializer

class competition_view_set(viewsets.ModelViewSet):
    serializer_class = CompetitionSerializer

    def get_queryset(self):
        current_date = timezone.now().date()
        queryset = Competition.objects.filter(date__gte=current_date).order_by('-date_created')[:100]
        return queryset

    # @read_only_scope
    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)

class survey_view_set(viewsets.ModelViewSet):
    queryset = Survey.objects.order_by('-date_created')[:100]
    serializer_class = SurveySerializer

class fest_view_set(viewsets.ModelViewSet):
    serializer_class = FestSerializer

    def get_queryset(self):
        current_date = timezone.now().date()
        queryset = Fest.objects.filter(date__gte=current_date).order_by('-date_created')[:100]
        return queryset

class seminar_view_set(viewsets.ModelViewSet):
    serializer_class = SeminarSerializer

    def get_queryset(self):
        current_date = timezone.now().date()
        queryset = Seminar.objects.filter(date__gte=current_date).order_by('-date_created')[:100]
        return queryset

class student_initiative_view_set(viewsets.ModelViewSet):
    queryset = StudentInitiative.objects.order_by('-date_created')[:100]
    serializer_class = StudentInitiativeSerializer

class alumni_view_set(viewsets.ModelViewSet):
    queryset = Alumni.objects.all()
    serializer_class = AlumniSerializer

def privacy_policy_url(request):
    return render(request, 'main/privacy-policy.html')

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def save_fcm_token(request):
    """API endpoint to save FCM token from Flutter app"""
    try:
        data = request.data
        user_email = data.get('user_email')
        fcm_token = data.get('fcm_token')
        platform = data.get('platform', 'android')
        app_version = data.get('app_version')

        if not user_email or not fcm_token:
            return Response({
                'success': False,
                'error': 'user_email and fcm_token are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update or create FCM token
        token_obj, created = UserFCMToken.objects.update_or_create(
            user_email=user_email,
            defaults={
                'fcm_token': fcm_token,
                'platform': platform,
                'app_version': app_version,
                'is_active': True
            }
        )

        # Create default notification preferences
        NotificationPreference.objects.get_or_create(
            user_email=user_email,
            defaults={
                'competitions_enabled': True,
                'seminars_enabled': True,
                'fests_enabled': True,
                'surveys_enabled': True,
                'student_initiatives_enabled': True,
                'alumni_enabled': True,
            }
        )

        logger.info(f"FCM token {'created' if created else 'updated'} for {user_email}")

        return Response({
            'success': True,
            'message': 'FCM token saved successfully'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error saving FCM token: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
@csrf_exempt
def update_notification_preferences(request):
    """API endpoint to update notification preferences"""
    try:
        data = request.data
        user_email = data.get('user_email')
        preferences = data.get('preferences', {})

        if not user_email:
            return Response({
                'success': False,
                'error': 'user_email is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update preferences
        pref_obj, created = NotificationPreference.objects.update_or_create(
            user_email=user_email,
            defaults={
                'competitions_enabled': preferences.get('events', True),
                'seminars_enabled': preferences.get('seminars', True),
                'fests_enabled': preferences.get('fests', True),
                'surveys_enabled': preferences.get('surveys', True),
                'student_initiatives_enabled': preferences.get('student_initiatives', True),
                'alumni_enabled': preferences.get('alumni', True),
            }
        )

        return Response({
            'success': True,
            'message': 'Notification preferences updated'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from firebase_admin import messaging
from django.http import JsonResponse
from .models import UserFCMToken


def send_test_notification(request):
    tokens = list(
        UserFCMToken.objects
        .filter(is_active=True)
        .values_list("fcm_token", flat=True)
    )

    if not tokens:
        return JsonResponse({"error": "No tokens found"}, status=400)

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title="Hello from Uniway 📢",
            body="New college update is available!",
        ),
        tokens=tokens,
    )

    response = messaging.send_each_for_multicast(message)

    for idx, resp in enumerate(response.responses):
        if not resp.success:
            print(f"❌ Failed token: {tokens[idx]}")
            print(f"Reason: {resp.exception}")

    return JsonResponse({
        "success": response.success_count,
        "failure": response.failure_count,
    })

