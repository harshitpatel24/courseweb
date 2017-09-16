from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from student import views

urlpatterns = [
    url(r'^$',views.student_panel,name='student_panel'),
    url(r'^edit/$', views.edit_profile, name='edit_profile'),
    url(r'^change_password/$', views.change_password, name='change_password'),
    url(r'^enrolled_course/$', views.enrolled_course, name='enrolled_course'),
    url(r'^question/+(?P<course_id>\d+)/$', views.ask_question_display, name='ask_question_display'),
    url(r'^ask/+(?P<course_id>\d+)/$', views.ask_question, name='ask_question'),
    url(r'^view_question/+(?P<question_id>\d+)/$', views.view_question, name='view_question'),
    url(r'^continue_conversation/+(?P<question_id>\d+)/$', views.continue_conversation, name='submit_question'),
    url(r'^question/all_questions/$', views.all_questions, name='ask_question_display'),
    url(r'^myprogress/$',views.myprogress,name='my_progress'),
    url(r'^accomplishments/$',views.accomplishments,name='accomplishments')

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.UPLOAD_URL, documnet_root=settings.UPLOAD_ROOT)