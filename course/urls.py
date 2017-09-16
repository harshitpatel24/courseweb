from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from course import views

urlpatterns = [

    url(r'^syllabus/+(?P<course_id>\d+)/$',views.syllabus,name='syllabus'),
    url(r'^quiz/start_quiz/+(?P<quiz_id>\d+)/$',views.start_quiz,name='start_quiz'),
    url(r'^quiz/submit_quiz/+(?P<quiz_id>\d+)/$',views.submit_quiz,name='submit_quiz'),
    url(r'^$',views.course_overview,name='courses'),
    url(r'^view_course/+(?P<course_id>\d+)/$',views.view_course,name='view_course'),
    url(r'^enroll/+(?P<course_id>\d+)/$',views.enroll,name='enroll'),
    url(r'^unenroll/$',views.unenroll,name='unenroll'),
    url(r'^announcements/+(?P<course_id>\d+)/$',views.all_announcement,name='announcements'),
    url(r'^payment/+(?P<course_id>\d+)/$', views.payment, name='enroll_payment'),
    url(r'^continue_pay/+(?P<course_id>\d+)/$', views.continue_pay, name='continue'),
    url(r'^mycourse/$',views.mycourse,name='mycourse'),
    url(r'^review1/+(?P<course_id>\d+)/$', views.review1, name='continue'),
    url(r'^rating_review/+(?P<course_id>\d+)/$', views.course_review, name='review'),
    url(r'^view_content/+(?P<course_name>[\w|\W]+)/+(?P<content_id>\d+)/$',views.contentdisplay,name='content_display'),
    url(r'^(?P<content_id>\d+)/+(?P<number>\d+)/$',views.videodisplay,name='video_display'),
    url(r'^quiz/+(?P<course_id>\d+)/+(?P<quiz_name>[\w|\W]+)/$',views.quiz1,name='quiz'),
    url(r'^certificate/+(?P<student_id>\d+)/+(?P<certificate_url>[\w|\W]+)/$', views.certificate1, name='certificate')

]