from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from instructor import views

urlpatterns = [
    url(r'^login/$',views.login,name='instructor_login'),
    url(r'^panel/$',views.instructor_panel,name='instructor_panel'),
    url(r'^createcourse/$',views.create_course,name='create_course'),
    url(r'^managecourse/$',views.managecourse,name='managecourse'),
    url(r'^managecourse/+(?P<course_id>\d+)+/$',views.edit_course,name='editcourse'),
    url(r'^logout/$',views.logout,name='instructor_logout'),
    url(r'^createcourse1/+(?P<course_id>\d+)+/$', views.create_course1, name='createcourse1'),
    url(r'^coursedisplay/+(?P<course_id>\d+)+/$',views.course_display,name='course_display'),
    url(r'^course_lock/+(?P<course_id>\d+)+/$',views.course_lock,name='course_lock'),
    url(r'^course_hide/+(?P<course_id>\d+)+/$',views.course_hide,name='course_hide'),
    url(r'^edit_main_content/+(?P<course_id>\d+)+/$',views.edit_main_content,name='edit_main_content'),
    url(r'^edit_sub_content/+(?P<course_id>\d+)+/$',views.edit_sub_content,name='edit_sub_content'),
    url(r'^delete_sub_content/+(?P<course_id>\d+)+/$',views.delete_sub_content,name='delete_sub_content'),
    url(r'^delete_main_content/+(?P<course_id>\d+)+/$',views.delete_main_content,name='delete_main_content'),
    url(r'^delete_course/+(?P<course_id>\d+)+/$',views.delete_course,name='delete_course'),

    url(r'^resources/+(?P<course_id>\d+)+/$',views.resources,name='resources'),
    url(r'^resource_detail/+(?P<resource_id>\d+)+/$',views.resource_detail,name='resource_detail'),
    url(r'^delete_resource/+(?P<resource_id>\d+)+/$',views.delete_resource,name='delete_resource'),

    url(r'^manage_sequence/+(?P<course_id>\d+)+/$',views.manage_sequence,name='manage_sequence'),
    url(r'^manage_sequence1/+(?P<course_id>\d+)+/$',views.manage_sequence1,name='manage_sequence1'),
    url(r'^move_up/+(?P<course_id>\d+)+/$',views.move_up,name='move_up'),
    url(r'^move_down/+(?P<course_id>\d+)+/$',views.move_down,name='move_down'),
    url(r'^instructor_profile/$',views.instructor_profile,name='instructor_profile'),
    url(r'^edit_profile/$',views.edit_profile,name='edit_profile'),
    url(r'^announcements/$',views.announcement,name='announcements'),
    url(r'^questions_panel/$',views.questions_panel,name='questions_panel'),
    url(r'^view_question/+(?P<question_id>\d+)+/$',views.view_question,name='view_question'),
    url(r'^reply_question/+(?P<question_id>\d+)+/$',views.reply_question,name='reply_question'),
    url(r'^create_questions/$',views.create_questions,name='create_questions'),
    url(r'^question_details/+(?P<question_id>\d+)+/$',views.question_details,name='question_details'),
    url(r'^delete_question/+(?P<question_id>\d+)+/$',views.delete_question,name='delete_question'),

    url(r'^delete_questions/+(?P<course_id>\d+)+/$',views.delete_questions,name='delete_questions'),

    url(r'^question_bank/$',views.question_bank,name='question_bank'),
    url(r'^question_bank1/+(?P<course_id>\d+)+/$',views.question_bank1,name='question_bank1'),
    url(r'^make_quiz/$',views.make_quiz,name='make_quiz'),
    url(r'^make_quiz1/$',views.make_quiz1,name='make_quiz1'),
    url(r'^quiz_display/$',views.quiz_display,name='quiz_display'),
    url(r'^quiz_display1/+(?P<course_id>\d+)+/$',views.quiz_display1,name='quiz_display1'),
    url(r'^quiz_details/+(?P<quiz_id>\d+)+/$',views.quiz_details,name='quiz_details'),
    url(r'^edit_quiz/+(?P<quiz_id>\d+)+/$',views.edit_quiz,name='edit_quiz'),
    url(r'^edit_quiz1/+(?P<quiz_id>\d+)+/$',views.edit_quiz1,name='edit_quiz1'),
    url(r'^delete_quiz/+(?P<quiz_id>\d+)+/$',views.delete_quiz,name='delete_quiz'),
    url(r'^lock_quiz/+(?P<quiz_id>\d+)+/$',views.lock_quiz,name='lock_quiz'),
    url(r'^hide_quiz/+(?P<quiz_id>\d+)+/$',views.hide_quiz,name='hide_quiz'),
    url(r'^earnings/$',views.earnings,name='earnings'),
    url(r'^students_enrolled/+(?P<course_id>\d+)+/$',views.students_enrolled,name='students_enrolled'),
    url(r'^managereview/$', views.managereview, name='managereview'),
    url(r'^approve/+(?P<review_id>\d+)+/$', views.approve, name='approve'),
    url(r'^remove/+(?P<review_id>\d+)+/$', views.remove, name='remove'),
    url(r'^sendmail/+(?P<course_id>\d+)+/$',views.sendmail,name='home'),
    url(r'^upload_csv/+(?P<course_id>\d+)+/$', views.upload_csv, name='upload_csv'),
    url(r'^faq/$', views.faqs, name='faq'),

    url(r'^faq_display/+(?P<course_id>\d+)+/$', views.faq_display, name='faq_display'),
    url(r'^delete_faq/+(?P<faq_id>\d+)+/$', views.delete_faq, name='delete_faq'),
]
