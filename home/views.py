from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from joinus.models import student,instructor
from instructor.models import enrolldata
from course.models import course

import os


def home(request):
        course_list = course.objects.all()
        instructor_list=instructor.objects.all()
        if 'userid' in request.session:
            obj=student.objects.get(pk=request.session['userid'])
            mycourse_list = enrolldata.objects.filter(student_id=obj)
            args={'username': obj.uname,
                  'course_list':course_list,
                  'status':'View Courses',
                  'link_status':'/course/',
                  'nav':'logout',
                  'student':obj,
                  'mycourselist':mycourse_list,
                  'instructor_list':instructor_list,}
            return render(request, 'home/home.html',args)
        else:
            args={'username':'Guest,Plz Login',
                  'course_list':course_list,
                  'status': 'Sign UP',
                  'nav':'register',
                  'link_status': '/joinus/register/',
                  'instructor_list':instructor_list}
            return render(request, 'home/home.html', args)

