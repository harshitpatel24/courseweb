# Create your views here.
import csv
import datetime
import os
from django.core.mail import send_mail
from django.db.models import Q, Max
from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from course.models import review, submissions
from coursewebsite import settings
from forum.models import Forum
from instructor.forms import add_questionForm, faq_Form
from instructor.models import course, coursecontent, enrolldata, announcements, difficulty_levels, add_question, quiz, \
    uploadcsv, faq, resource_type, resources1, categories
from joinus.models import student, instructor
from student.models import askquestion
import itertools

def login(request):
    if 'instructorid' in request.session:
        obj = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = obj.uname
        args = {  # 'instructor': globals()['loggedin'],
                  'instructor': obj,
                  'instructorname': instructorname,
                  }
        return HttpResponseRedirect('/instructor/panel/', args)
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('pass')
            instructors = instructor.objects.all()
            for instructor_data in instructors:
                if password == instructor_data.password and email == instructor_data.email:
                    #  globals()['loggedin']=instructor_data
                    request.session['instructorid'] = instructor_data.pk
                    obj = instructor.objects.get(pk=request.session['instructorid'])
                    instructorname = obj.uname
                    args = {'instructor': obj,
                            'instructorname': instructorname}
                    return HttpResponseRedirect('/instructor/panel/', args)
            return render(request, 'instructor/instructor_login.html',
                          {'message': 'Wrong Username or Password', 'instructorname': 'Guest,Plz Login'})
        else:
            return render(request, 'instructor/instructor_login.html', {'instructorname': 'Guest,Plz Login'})


def logout(request):
    del request.session['instructorid']
    return HttpResponseRedirect('/home/')


def managecourse(request):
    if request.session.get('instructorid') != None:
        obj = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = obj.uname
        args = {
            # 'instructor': globals()['loggedin'],
            'instructorname': instructorname,
            'user1': obj, }
        return render(request, 'instructor/manage_course.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')


def instructor_panel(request):
    if request.session.get('instructorid') != None:
        obj = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = obj.uname
        courses = course.objects.filter(creatorid=obj.id).values_list('id', flat=True)
        enrollobj = enrolldata.objects.filter(course_id__in=courses)
        enrolls = enrollobj.count()
        total = 0
        for temp in enrollobj:
            if temp.fee_status != 'n':
                obj1 = course.objects.get(id=temp.course_id.id)
                total = total + obj1.fee
        args = {'user1': obj,
                'enrolls': enrolls,
                'instructorname': instructorname,
                'courses_created': courses.count(),
                'earnings': total}

        return render(request, 'instructor/instructor_panel.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')


def edit_course(request, course_id):
    if request.session.get('instructorid') != None:
        if request.method == 'POST':
            data = course.objects.get(pk=course_id)
            data.cname = request.POST.get('coursename')
            data.cdesc = request.POST.get('coursedesc')
            data.taughtby = request.POST.get('taughtby')
            data.prerequisite = request.POST.get('prerequisites')
            data.courselanguage = request.POST.get('courselanguage')
            data.duration = request.POST.get('duration')
            data.fee = request.POST.get('fee')
            data.startdate = request.POST.get('startdate')
            data.end_date = request.POST.get('enddate')
            data.category_id = request.POST.get('category')
            if request.FILES:
                data.course_pic = request.FILES['course_pic']
            else:
                data.course_pic = request.POST.get('course_pic1')
            data.save()
            courseid = course.objects.get(id=course_id)
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0)
            contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0)
            courseobj = course.objects.get(id=courseid.id)

            obj = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = obj.uname
            args1 = {
                # 'instructor': request.session['instructorid'],
                'instructor': obj,
                'course': courseobj,
                'content': contentobj,
                'instructorname': instructorname,
                'subcontent': contentobj1,
                'message': 'success',
            }
            return HttpResponseRedirect(reverse(course_display,args=course_id))
            #return render(request, 'instructor/course_display.html', args1)
        else:
            data = course.objects.get(pk=course_id)
            obj = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = obj.uname
            args2 = {
                # 'instructor': request.session['instructorid'],
                'instructor': obj,
                'course': data,
                'categories':categories.objects.all()
            }
            return render(request, 'instructor/edit_course.html', args2)
    else:
        return HttpResponseRedirect('/instructor/login/')


def create_course(request):
    if request.session.get('instructorid') != None:
        if request.method == 'POST':
            cname = request.POST.get('coursename')
            cdesc = request.POST.get('coursedesc')
            taughtby = request.POST.get('taughtby')
            prerequisite = request.POST.get('prerequisites')
            courselanguage = request.POST.get('courselanguage')
            duration = request.POST.get('duration')
            fee = request.POST.get('fee')
            startdate = request.POST.get('startdate')
            enddate = request.POST.get('enddate')
            pic = request.FILES['course_pic']
            category_obj = categories.objects.get(pk=request.POST.get('category'))
            data = instructor.objects.get(pk=request.session['instructorid'])
            createdby = data
            courseobject = course(cname=cname,category_id=category_obj ,creatorid=createdby, cdesc=cdesc, taughtby=taughtby,
                                  prerequisite=prerequisite,
                                  course_language=courselanguage, duration=duration, fee=fee, start_date=startdate,end_date=enddate,
                                  course_pic=pic,lock=0,hide=0)
            courseobject.save()
            forum_obj = Forum(title=cname, description=cdesc, creator=data,courseid=courseobject)
            forum_obj.save()
            course_content = coursecontent.objects.all()
            instructorobj = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = instructorobj.uname
            args = {'instructor': instructorobj, 'instructorname': instructorname,
                    'message': 'success', 'course_id': courseobject.id, 'course_content': course_content,
                    'categories':categories.objects.all()}
            return render(request, 'instructor/create_course1.html', args)
        else:
            instructorobj = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = instructorobj.uname
            args = {'instructor': request.session['instructorid'], 'instructorname': instructorname,
                    'instructorobj': instructorobj,
                    'categories':categories.objects.all()}
            return render(request, 'instructor/create_course.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')


def create_course1(request, course_id):
    if request.session.get('instructorid') != None:
        if request.method == 'POST':

            courseid = request.POST.get('course_id')
            data = course.objects.get(pk=courseid)
            contentobj = coursecontent.objects.filter(course_id=data)
            count = 0
            count1 = 0
            type = 'video'
            seq_no = 0
            file = 'null'
            message = None
            topic1 = request.POST.get('maintopicname')
            if topic1 is not None:
                seq_obj = coursecontent.objects.filter(course_id=data).order_by('-content_sequence_no').first()
                name = request.POST.get('maintopicname')
                desc = request.POST.get('maintopicdesc')
                if request.FILES:
                    file = request.FILES['content_file']

                subid = 0
                if seq_obj is not None:
                    seq_no = seq_obj.content_sequence_no + 1
            else:
                subid = int(request.POST.get('maintopicname1'))
                seq_obj = coursecontent.objects.filter(course_id=data,content_sub_id=subid).order_by('-content_sequence_no').first()
                name = request.POST.get('subtopicname')
                desc = request.POST.get('subtopicdesc')
                if request.FILES['content_file'] is not None:
                    file = request.FILES['content_file']
                if seq_obj is not None:
                    seq_no = seq_obj.content_sequence_no + 1
                # subid=coursecontent.objects.get(pk=subid1)
                createdby = request.session['instructorid']

            if message is  None:
                contentobject = coursecontent(course_id=data, content_sub_id=subid, content_name=name,
                                              content_description=desc, content_type=type, content_url=file,
                                              content_sequence_no=seq_no,)
                contentobject.save()
            return HttpResponseRedirect(reverse(course_display,args=course_id))
            #return render(request, 'instructor/instructor_panel.html', args)
        else:
            courseid = course.objects.get(pk=course_id)
            course_content1 = coursecontent.objects.filter(course_id=courseid, content_sub_id=0)
            # course_content=coursecontent.objects.all()
            instructorobj = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = instructorobj.uname
            args = {'instructor': instructorobj, 'course_id': course_id,
                    'instructorname': instructorname,
                    'course_content': course_content1}
            return render(request, 'instructor/create_course1.html/', args)
    else:
        return HttpResponseRedirect('/instructor/login/')


def course_display(request, course_id):
    if request.session.get('instructorid') != None:
        if request.method == 'POST':
            courseid = course.objects.get(pk=course_id)
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by(
                'content_sequence_no')
            contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0).order_by(
                'content_sequence_no')
            courseobj = course.objects.get(id=courseid.id)


            # print(coursecontent._meta.pk.name)
            data = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = data.uname
            args = {'instructor': request.session['instructorid'],
                    'user1': data,
                    'instructorname': instructorname,
                    'message': 'success',
                    'course': courseobj,
                    'content': contentobj,
                    'subcontent': contentobj1,
                    }
            return render(request, 'instructor/course_display.html', args)
        else:
            courseid = course.objects.get(pk=course_id)
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by(
                'content_sequence_no')
            contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0).order_by(
                'content_sequence_no')
            courseobj = course.objects.get(id=courseid.id)
            difficulty_obj = difficulty_levels.objects.all()
            data = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = data.uname
            args = {'instructor': request.session['instructorid'],
                    'user1': data,
                    'message': 'success',
                    'instructorname': instructorname,
                    'course': courseobj,
                    'content': contentobj,
                    'subcontent': contentobj1,
                    'difficulty':difficulty_obj}
            return render(request, 'instructor/course_display.html', args)
    else:
        return HttpResponseRedirect('/instructor/coursedisplay/')

def course_lock(request,course_id):
    if request.session.get('instructorid') != None:
        courseid = course.objects.get(pk=course_id)
        courseid.lock = 1
        courseid.save()
        courseid = course.objects.get(pk=course_id)
        contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by('content_sequence_no')
        contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0).order_by('content_sequence_no')
        courseobj = course.objects.get(id=courseid.id)
        difficulty_obj = difficulty_levels.objects.all()
        data = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = data.uname
        args = {'instructor': request.session['instructorid'],
                    'user1': data,
                    'message': 'success',
                    'instructorname': instructorname,
                    'course': courseobj,
                    'content': contentobj,
                    'subcontent': contentobj1,
                    'difficulty':difficulty_obj}
        return HttpResponseRedirect(reverse(course_display,args=str(course_id)))
        #return render(request, 'instructor/course_display.html', args)
    else:
        return HttpResponseRedirect('/instructor/coursedisplay/')

def course_hide(request,course_id):
    if request.session.get('instructorid') != None:
        courseid = course.objects.get(pk=course_id)
        if courseid.hide=="0":
            courseid.hide="1"
        else:
            courseid.hide="0"
        courseid.save()
        courseid = course.objects.get(pk=course_id)
        contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by('content_sequence_no')
        contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0).order_by('content_sequence_no')
        courseobj = course.objects.get(id=courseid.id)
        difficulty_obj = difficulty_levels.objects.all()
        data = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = data.uname
        args = {'instructor': request.session['instructorid'],
                    'user1': data,
                    'message': 'success',
                    'instructorname': instructorname,
                    'course': courseobj,
                    'content': contentobj,
                    'subcontent': contentobj1,
                    'difficulty':difficulty_obj}
        return HttpResponseRedirect(reverse(course_display,args=str(course_id)))
        #return render(request, 'instructor/course_display.html', args)
    else:
        return HttpResponseRedirect('/instructor/coursedisplay/')

def edit_main_content(request, course_id):
    if request.session.get('instructorid') != None:
        if request.method == 'POST':
            contentobj = coursecontent.objects.get(pk=course_id, content_sub_id=0)
            contentobj.content_name = request.POST.get('content_name')
            contentobj.content_description = request.POST.get('content_desc')
            contentobj.save()
            courseid = coursecontent.objects.get(id=course_id)

            contentobj = coursecontent.objects.filter(course_id=courseid.course_id.id, content_sub_id=0)
            contentobj1 = coursecontent.objects.filter(course_id=courseid.course_id.id).exclude(content_sub_id=0)
            courseobj = course.objects.get(id=courseid.course_id.id)
            data = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = data.uname
            args = {'instructor': request.session['instructorid'],
                    'user1': data,
                    'message': 'success',
                    'course': courseobj,
                    'instructorname': instructorname,
                    'content': contentobj,
                    'subcontent': contentobj1
                    }
            return HttpResponseRedirect(reverse(course_display,args=str(courseid.course_id.id)))
            #return render(request, 'instructor/course_display.html', args)
        else:
            courseid = coursecontent.objects.get(pk=course_id)
            contentobj = coursecontent.objects.get(id=courseid.id, content_sub_id=0)
            contentobj1 = coursecontent.objects.filter(content_sub_id=contentobj.id)
            # courseobj = course.objects.get(id=courseid.id)

            # print(coursecontent._meta.pk.name)
            data = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = data.uname
            args = {'instructor': request.session['instructorid'],
                    'user1': data,
                    'message': 'success',
                    #  'course': courseobj,
                    'instructorname': instructorname,
                    'content': contentobj,
                    'subcontent': contentobj1}
            return render(request, 'instructor/edit_main_content.html', args)
    else:
        return HttpResponseRedirect('/instructor/coursedisplay/')


def edit_sub_content(request, course_id):
    if request.session.get('instructorid') != None:
        if request.method == 'POST':
            contentobj = coursecontent.objects.get(pk=course_id)
            contentobj.content_name = request.POST.get('content_name')
            contentobj.content_description = request.POST.get('content_desc')
            if request.FILES:
                contentobj.content_url = request.FILES['content_file']
            else:
                contentobj.content_url = request.POST.get('content_file1')
            contentobj.save()
            courseid = coursecontent.objects.get(id=course_id)

            contentobj = coursecontent.objects.filter(course_id=courseid.course_id.id, content_sub_id=0)
            contentobj1 = coursecontent.objects.filter(course_id=courseid.course_id.id).exclude(content_sub_id=0)
            courseobj = course.objects.get(id=courseid.course_id.id)
            data = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = data.uname
            args = {'instructor': request.session['instructorid'],
                    'user1': data,
                    'instructorname': instructorname,
                    'message': 'success',
                    'course': courseobj,
                    'content': contentobj,
                    'subcontent': contentobj1
                    }
            return HttpResponseRedirect(reverse(course_display,args=str(courseid.course_id.id)))
            #return render(request, 'instructor/course_display.html', args)
        else:
            contentobj = coursecontent.objects.get(id=course_id)
            data = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = data.uname
            args = {'instructor': request.session['instructorid'],
                    'user1': data,
                    'message': 'success',
                    'instructorname': instructorname,
                    'subcontent': contentobj,
                    }
            return render(request, 'instructor/edit_sub_content.html', args)
    else:
        return HttpResponseRedirect('/instructor/coursedisplay/')


def manage_sequence(request, course_id):
    if request.session.get('instructorid') != None:
        if request.method == 'POST':
            courseid = course.objects.get(pk=course_id)
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by(
                'content_sequence_no')
            courseobj = course.objects.get(id=courseid.id)

            # print(coursecontent._meta.pk.name)
            data = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = data.uname
            args = {'instructor': request.session['instructorid'],
                    'user1': data,
                    'message': 'success',
                    'course': courseobj,
                    'instructorname': instructorname,
                    'content': contentobj,
                    }
            return render(request, 'instructor/course_display.html', args)
        else:
            courseid = course.objects.get(pk=course_id)
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by(
                'content_sequence_no')

            courseobj = course.objects.get(id=courseid.id)

            data = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = data.uname
            args = {'instructor': request.session['instructorid'],
                    'user1': data,
                    'message': 'success',
                    'course': courseobj,
                    'instructorname': instructorname,
                    'content': contentobj,
                    }
            return render(request, 'instructor/manage_sequence.html', args)
    else:
        return HttpResponseRedirect('/instructor/manage_sequence/')


def manage_sequence1(request, course_id):
    if request.session.get('instructorid') != None:
        if request.method == 'POST':
            courseid = coursecontent.objects.get(pk=course_id)
            contentobj = coursecontent.objects.filter(content_sub_id=courseid.id).order_by('content_sequence_no')
            courseobj = course.objects.get(id=contentobj.course_id)

            # print(coursecontent._meta.pk.name)
            data = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = data.uname
            args = {'instructor': request.session['instructorid'],
                    'user1': data,
                    'message': 'success',
                    'instructorname': instructorname,
                    'course': courseobj,
                    'content': contentobj,
                    }
            return render(request, 'instructor/course_display.html', args)
        else:
            courseid = coursecontent.objects.get(pk=course_id)
            contentobj = coursecontent.objects.filter(content_sub_id=courseid.id).order_by('content_sequence_no')
            courseobj = course.objects.get(id=courseid.course_id.id)

            data = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = data.uname
            args = {'instructor': request.session['instructorid'],
                    'user1': data,
                    'message': 'success',
                    'instructorname': instructorname,
                    'course': courseobj,
                    'content': contentobj,
                    }
            return render(request, 'instructor/manage_sequence.html', args)
    else:
        return HttpResponseRedirect('/instructor/manage_sequence/')

@csrf_exempt
def move_up(request, course_id):
    #if request.session.get('instructorid') != None:
        courseid = coursecontent.objects.get(id=course_id)
        temp = courseid.content_sequence_no
        if courseid.content_sub_id == 0:
            if temp - 1 > 0:
                temp1 = coursecontent.objects.get(content_sequence_no=temp - 1, content_sub_id=0,
                                                  course_id=courseid.course_id)
                courseid.content_sequence_no = temp - 1
                courseid.save()
                temp1.content_sequence_no = temp
                temp1.save()
                courseid = coursecontent.objects.get(pk=course_id)
            contentobj = coursecontent.objects.filter(course_id=courseid.course_id.id, content_sub_id=0).order_by(
                'content_sequence_no')
        else:
            if temp - 1 > 0:
                temp1 = coursecontent.objects.get(~Q(content_sub_id=0), content_sequence_no=temp - 1,
                                                  course_id=courseid.course_id, content_sub_id=courseid.content_sub_id)
                courseid.content_sequence_no = temp - 1
                courseid.save()
                temp1.content_sequence_no = temp
                temp1.save()
                courseid = coursecontent.objects.get(pk=course_id)
            contentobj = coursecontent.objects.filter(~Q(content_sub_id=0), course_id=courseid.course_id.id).order_by(
                'content_sequence_no')

        courseobj = course.objects.get(id=courseid.course_id.id)
        data = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = data.uname
        args = {'instructor': request.session['instructorid'],
                'user1': data,
                'message': 'success',
                'course': courseobj,
                'instructorname': instructorname,
                'content': contentobj,
                }
        return render(request, 'instructor/refresh.html', args)

@csrf_exempt
def move_down(request, course_id):
    if request.session.get('instructorid') != None:
        courseid = coursecontent.objects.get(pk=course_id)
        temp = courseid.content_sequence_no

        if courseid.content_sub_id == 0:
            max_obj = coursecontent.objects.filter(course_id=courseid.course_id.id, content_sub_id=0).order_by(
                'content_sequence_no')
            max = max_obj.latest('content_sequence_no')
            if temp + 1 <= max.content_sequence_no:
                temp1 = coursecontent.objects.get(content_sequence_no=temp + 1, content_sub_id=0,
                                                  course_id=courseid.course_id)
                courseid.content_sequence_no = temp + 1
                courseid.save()
                temp1.content_sequence_no = temp
                temp1.save()

                courseid = coursecontent.objects.get(pk=course_id)

            contentobj = coursecontent.objects.filter(course_id=courseid.course_id.id, content_sub_id=0).order_by(
                'content_sequence_no')
        else:
            max_obj = coursecontent.objects.filter(course_id=courseid.course_id.id).exclude(content_sub_id=0).order_by(
                'content_sequence_no')
            max = max_obj.latest('content_sequence_no')
            if temp + 1 <= max.content_sequence_no:
                temp1 = coursecontent.objects.get(~Q(content_sub_id=0), content_sequence_no=temp + 1,
                                                  course_id=courseid.course_id)
                courseid.content_sequence_no = temp + 1
                courseid.save()
                temp1.content_sequence_no = temp
                temp1.save()

                courseid = coursecontent.objects.get(pk=course_id)

            contentobj = coursecontent.objects.filter(~Q(content_sub_id=0), course_id=courseid.course_id.id).order_by(
                'content_sequence_no')
        courseobj = course.objects.get(id=courseid.course_id.id)

        data = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = data.uname
        args = {'instructor': request.session['instructorid'],
                'user1': data,
                'message': 'success',
                'course': courseobj,
                'instructorname': instructorname,
                'content': contentobj,
                }
        return render(request, 'instructor/refresh.html', args)
        #return render(request, 'instructor/manage_sequence.html', args)
    else:
        courseid = coursecontent.objects.get(pk=course_id)
        return HttpResponseRedirect('/instructor/manage_sequence/')


def delete_sub_content(request, course_id):
    if request.session.get('instructorid') != None:
        contentobj = coursecontent.objects.get(pk=course_id)
        courseid = coursecontent.objects.get(id=course_id)
        contentobj.delete()
        contentobj = coursecontent.objects.filter(course_id=courseid.course_id.id, content_sub_id=0)
        contentobj1 = coursecontent.objects.filter(course_id=courseid.course_id.id).exclude(content_sub_id=0)
        courseobj = course.objects.get(id=courseid.course_id.id)
        data = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = data.uname
        args = {'instructor': request.session['instructorid'],
                'user1': data,
                'message': 'success',
                'course': courseobj,
                'instructorname': instructorname,
                'content': contentobj,
                'subcontent': contentobj1
                }
        return HttpResponseRedirect(reverse(course_display,args=str(courseid.course_id.id)))
        #return render(request, 'instructor/course_display.html', args)
    else:
        return HttpResponseRedirect('/instructor/coursedisplay/')


def delete_main_content(request, course_id):
    if request.session.get('instructorid') != None:
        contentobj = coursecontent.objects.get(pk=course_id)
        courseid = coursecontent.objects.get(id=course_id)
        contentobj.delete()
        temp = coursecontent.objects.filter(content_sub_id=courseid.id)
        temp.delete()
        contentobj = coursecontent.objects.filter(course_id=courseid.course_id.id, content_sub_id=0)
        contentobj1 = coursecontent.objects.filter(course_id=courseid.course_id.id).exclude(content_sub_id=0)
        courseobj = course.objects.get(id=courseid.course_id.id)
        data = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = data.uname
        args = {'instructor': request.session['instructorid'],
                'user1': data,
                'message': 'success',
                'course': courseobj,
                'instructorname': instructorname,
                'content': contentobj,
                'subcontent': contentobj1
                }
        return HttpResponseRedirect(reverse(course_display,args=str(courseid.course_id.id)))
        #return render(request, 'instructor/course_display.html', args)
    else:
        return HttpResponseRedirect('/instructor/coursedisplay/')


def delete_course(request, course_id):
    if request.session.get('instructorid') != None:
        course1 = course.objects.get(id=course_id)
        course1.delete()

        obj = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = obj.uname
        args = {'user1': obj,
                'instructorname': instructorname, }
        return HttpResponseRedirect(reverse(instructor_panel))
        #return render(request, 'instructor/instructor_panel.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def resources(request, course_id):
    if request.session.get('instructorid') != None:
        if request.method == 'POST':
            flag=0
            url = ""
            file = ""
            if request.FILES:
                file = request.FILES['content_file']
            name = request.POST.get('name')
            description = request.POST.get('desc')
            if request.POST.get('enter_url') :
                url = request.POST.get('enter_url')
            content_obj = coursecontent.objects.get(pk=course_id)
            type = resource_type.objects.get(id=request.POST.get('type'))
            resource_obj = resources1.objects.filter(content_id=course_id).order_by('-sequence_no').first()
            #for r in resource_obj:
            #    count=count+1
            seq_no = 0
            if resource_obj is not None:
                seq_no=resource_obj.sequence_no + 1
            resource_obj1 = resources1(content_id=content_obj,name=name,type=type,description=description,content_url1=file,content_url2=url,sequence_no=seq_no)
            resource_obj1.save()

            return HttpResponseRedirect(reverse(resources,args=(course_id,)))
        else:
            try:
                resource_obj = resources1.objects.filter(content_id=course_id)
            except:
                resource_obj = None

            content_obj = coursecontent.objects.get(id=course_id)
            type_obj = resource_type.objects.all()
            obj = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = obj.uname
            args = {'user1': obj,
                    'instructorname': instructorname,
                    'mcontent':content_obj,
                    'content':resource_obj,
                    'id':content_obj,
                    'types':type_obj}
            #return HttpResponseRedirect(reverse(instructor_panel))
            return render(request, 'instructor/resources.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def resource_detail(request,resource_id):
    if request.session.get('instructorid') != None:
        resource_obj = resources1.objects.get(id=resource_id)
        obj = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = obj.uname
        args = {'user1': obj,
                    'instructorname': instructorname,
                    'content':resource_obj,
                }
        #return HttpResponseRedirect(reverse(instructor_panel))
        return render(request, 'instructor/resource_detail.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def delete_resource(request,resource_id):
    if request.session.get('instructorid') != None:
        resource_obj = resources1.objects.get(id=resource_id)
        course_id = resource_obj.content_id.id
        resource_obj.delete()
        return HttpResponseRedirect(reverse(resources,args=(course_id,)))
        #return render(request, 'instructor/resource_detail.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')


def instructor_profile(request):
    if request.session.get('instructorid') != None:
        obj = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = obj.uname
        args = {'user1': obj,
                'instructorname': instructorname, }
        return render(request, 'instructor/instructor_profile.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')


def edit_profile(request):
    if request.session.get('instructorid') != None:
        if request.method == 'POST':
            obj = instructor.objects.get(pk=request.session['instructorid'])
            if request.FILES:
                pic = request.FILES['file1']
            else:
                pic = request.POST.get('file2')
            obj.fname = request.POST.get('fname')
            obj.lname = request.POST.get('lname')
            obj.uname = request.POST.get('uname')
            obj.pic = pic
            obj.save()
            obj = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = obj.uname
            args = {'user1': obj,
                    'instructorname': instructorname, }
            return HttpResponseRedirect(reverse(instructor_profile))
            #return render(request, 'instructor/instructor_profile.html', args)
        else:
            obj = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = obj.uname
            args = {'user1': obj,
                    'instructorname': instructorname, }
            return render(request, 'instructor/edit_profile.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')


def announcement(request):
    if request.session.get('instructorid') != None:
        if request.method == 'POST':
            title1 = request.POST.get('title')
            desc1 = request.POST.get('desc')
            course_id = request.POST.get('courses')
            data = course.objects.get(pk=course_id)
            print(data.id)
            print(title1)
            print(desc1)
            date1 = str(datetime.datetime.now().strftime("%d/%m/%Y"))
            time1 = str(datetime.datetime.now().strftime("%H:%M"))
            announcements_obj = announcements(course_id=data, title=title1, description=desc1,
                                              Adate=date1,
                                              Atime=time1)
            announcements_obj.save()
            obj = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = obj.uname
            args = {'user1': obj,
                    'instructorname': instructorname, }
            return HttpResponseRedirect(reverse(instructor_panel))
            #return render(request, 'instructor/instructor_panel.html', args)
        else:
            obj = instructor.objects.get(pk=request.session['instructorid'])
            courses = course.objects.filter(creatorid=request.session['instructorid'])
            instructorname = obj.uname
            args = {'user1': obj,
                    'courses': courses,
                    'instructorname': instructorname, }
            return render(request, 'instructor/announcements.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')


def questions_panel(request):
    remaining = askquestion.objects.filter(question_subid=0,
                                           instructor_id=instructor.objects.get(pk=request.session.get('instructorid')),
                                           question_flag='y').order_by('course_id__cname')
    courses = askquestion.objects.filter(question_subid=0,
                                         instructor_id=instructor.objects.get(pk=request.session.get('instructorid'))).values(
        'course_id__cname').distinct()
    b=[]
    for remain in remaining:
        b.append(remain.course_id.cname)
    a=[]
    for course in courses:
        for k,v in course.items():
            a.append(v)
            a.append(b.count(v))
    a.append('general')
    a.append(len(remaining))
    d = dict(itertools.zip_longest(*[iter(a)] * 2, fillvalue=""))
    #print(d)
    questions = askquestion.objects.filter(instructor_id=instructor.objects.get(pk=request.session.get('instructorid')),
                                           question_subid=0).order_by('-question_flag')

    #courses = askquestion.objects.filter(question_subid=0,
    #                                     student_id=student.objects.get(pk=request.session.get('userid'))).values(
    #    'course_id__cname').distinct()
    return render(request, 'instructor/questions_panel.html', {'questions': questions, 'remaining': d,'courses':courses})


def view_question(request, question_id):
    question_data = askquestion.objects.filter(Q(question_subid=question_id) | Q(pk=question_id))
    return render(request, 'instructor/view_question.html', {'question_data': question_data})


def reply_question(request, question_id):
    reply = request.POST.get('reply')
    data = askquestion.objects.get(pk=question_id)
    askquestion.objects.filter(pk=question_id).update(reply_description=reply,
                                                      reply_date=str(datetime.datetime.now().strftime("%d/%m/%Y")),
                                                      reply_time=str(datetime.datetime.now().strftime("%H:%M")))

    if data.question_subid == 0:
        askquestion.objects.filter(pk=question_id).update(question_flag='n', reply_flag='y')
        question_data = askquestion.objects.filter(Q(question_subid=question_id) | Q(pk=question_id))

        return render(request, 'instructor/view_question.html', {'question_data': question_data})
    else:
        askquestion.objects.filter(pk=data.question_subid).update(question_flag='n', reply_flag='y')
        question_data = askquestion.objects.filter(Q(question_subid=data.question_subid) | Q(pk=data.question_subid))
        return render(request, 'instructor/view_question.html', {'question_data': question_data})


def create_questions(request):
    if request.session.get('instructorid') != None:
        form = add_questionForm
        if request.method == 'POST':
            difficulty_obj = difficulty_levels.objects.all()
            type = request.POST.get('type')
            course_id = request.POST.get('coursename')
            if request.POST.get('from') == None:
                if request.POST.get('question') == "":
                    option11 = ""
                    option12 = ""
                    option13 = ""
                    option14 = ""
                    question = request.POST.get('question')
                    answer = request.POST.get('answer')
                    feedbackc = request.POST.get('feedbackc')
                    feedbackw = request.POST.get('feedbackw')
                    hint = request.POST.get('hint')
                    if type != '1':
                        option11 = request.POST.get('choice1')
                        option12 = request.POST.get('choice2')
                        option13 = request.POST.get('choice3')
                        option14 = request.POST.get('choice4')
                    course_obj = course.objects.get(pk=course_id)
                    obj = instructor.objects.get(pk=request.session['instructorid'])
                    instructorname = obj.uname
                    args = {'user1': obj,
                                'course': course_obj,
                                'type': type,
                                'form': form,
                                'instructorname': instructorname,
                                'difficulty': difficulty_obj,
                                'mode':'error',
                            'option1':option11,'option2':option12,'option3':option13,'option4':option14,
                            'question':question,'answer':answer,'feedbackc':feedbackc,'feedbackw':feedbackw,'hint':hint}
                    return render(request, 'instructor/create_questions.html', args)
                else:
                    question = request.POST.get('question')
                    answer = request.POST.get('answer')
                    feedbackc = request.POST.get('feedbackc')
                    feedbackw = request.POST.get('feedbackw')
                    hint = request.POST.get('hint')
                    difficulty = request.POST.get('difficulty')
                    if type != '1':
                        option11 = request.POST.get('choice1')
                        option12 = request.POST.get('choice2')
                        option13 = request.POST.get('choice3')
                        option14 = request.POST.get('choice4')
                        idd = course.objects.get(pk=course_id)
                        did = difficulty_levels.objects.get(pk=int(difficulty))
                        question_obj = add_question(course_id=idd, question=question, answer=answer, feedbackc=feedbackc,
                                                    feedbackw=feedbackw, hint=hint, difficulty=did, question_type=type,
                                                    option1=option11, option2=option12, option3=option13, option4=option14)
                        question_obj.save()
                        return HttpResponseRedirect(reverse(question_bank1,args=(course_id,)))
                    else:
                        idd = course.objects.get(pk=course_id)
                        did = difficulty_levels.objects.get(pk=int(difficulty))
                        question_obj = add_question(course_id=idd, question=question, answer=answer, feedbackc=feedbackc,
                                                    feedbackw=feedbackw, hint=hint, difficulty=did, question_type=type)
                        question_obj.save()
                        return HttpResponseRedirect(reverse(question_bank1,args=(course_id,)))
            course_obj = course.objects.get(pk=course_id)
            obj = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = obj.uname
            args = {'user1': obj,
                        'course': course_obj,
                        'type': type,
                        'form': form,
                        'instructorname': instructorname,
                        'difficulty': difficulty_obj,
                        'mode':'first_time',
                    'option1':"",'option2':"",'option3':"",'option4':"",
                            'question':"",'answer':"",'feedbackc':"",'feedbackw':"",'hint':""}
            return render(request, 'instructor/create_questions.html', args)
        else:
            obj = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = obj.uname
            args = {'user1': obj,
                    'instructorname': instructorname,
                    'form': form,
                    }
            return HttpResponseRedirect(reverse(create_questions))
            #return render(request, 'instructor/create_questions.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def question_bank(request):
    if request.session.get('instructorid') != None:
        questions = add_question.objects.all()
        obj = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = obj.uname
        args = {'user1': obj,
                'instructorname': instructorname,
                'questions': questions
                }
        return render(request, 'instructor/question_bank.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def question_bank1(request,course_id):
    if request.session.get('instructorid') != None:
        questions = add_question.objects.filter(course_id=course_id)
        contentobj = coursecontent.objects.filter(course_id=course_id, content_sub_id=0).order_by(
                'content_sequence_no')
        difficulty_obj = difficulty_levels.objects.all()
        obj = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = obj.uname
        args = {'user1': obj,
                'instructorname': instructorname,
                'questions': questions,
                'cname':course_id,
                'content':contentobj,
                'difficulty':difficulty_obj
                }
        return render(request, 'instructor/question_bank.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')


def question_details(request,question_id):
    if request.session.get('instructorid') != None:
        question = add_question.objects.get(id=question_id)
        obj = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = obj.uname
        args = {'user1': obj,
                'instructorname': instructorname,
                'q': question
                }
        return render(request, 'instructor/question_details.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def delete_question(request,question_id):
    if request.session.get('instructorid') != None:
        question = add_question.objects.get(id=question_id)
        course_id = question.course_id
        idd = question.course_id.id
        question.delete()
        questions = add_question.objects.filter(course_id=course_id)
        obj = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = obj.uname
        args = {'user1': obj,
                'instructorname': instructorname,
                'questions': questions
                }
        return HttpResponseRedirect(reverse(question_bank1,args=(idd,)))
        #return render(request, 'instructor/question_bank.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def delete_questions(request,course_id):
    if request.session.get('instructorid') != None:
        list = request.POST.getlist('selected_questions')
        question = add_question.objects.filter(id__in=list)
        if request.POST.get('mode1') == "export":
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
            writer = csv.writer(response)
            for q in question:
                writer.writerow([q.question,q.option1,q.option2,q.option3,q.option4,q.answer,q.feedbackc,q.feedbackw,q.hint,q.difficulty.id,q.question_type])
            #writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
            #writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])
            return response
        else:
            question.delete()
            questions = add_question.objects.filter(course_id=course_id)
            obj = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = obj.uname
            args = {'user1': obj,
                    'instructorname': instructorname,
                    'questions': questions
                    }
            return HttpResponseRedirect(reverse(question_bank1,args=(course_id,)))
        #return render(request, 'instructor/question_bank.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')


def make_quiz(request):
    if request.session.get('instructorid') != None:
        print(request.POST.get('content'))
        content1 = coursecontent.objects.get(pk=request.POST.get('content'))

        difficulty = request.POST.get('difficulty')
        did = difficulty_levels.objects.get(pk=int(difficulty))

        questions = add_question.objects.filter(course_id=content1.course_id,difficulty=did.id)

        obj = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = obj.uname
        args = {'user1': obj,
                'instructorname': instructorname,
                'questions': questions,
                'difficulty':did,
                'content':content1,
                }
        return render(request, 'instructor/make_quiz.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def make_quiz1(request):
    if request.session.get('instructorid') != None:
        mode=request.POST.get('mode')
        obj = instructor.objects.get(pk=request.session['instructorid'])
        if mode == 'make_quiz':
            content = coursecontent.objects.get(pk=request.POST.get('content'))
            question_list = request.POST.getlist('selected_questions')
            questions = add_question.objects.filter(id__in=question_list)
            quiz_obj = quiz.objects.filter(content_id=content.id,lock='1')
            total=0
            for q in quiz_obj:
                total = total + int(q.quiz_weightage)
            remaining = 100 - total
            difficulty = request.POST.get('difficulty')
            did = difficulty_levels.objects.get(name=difficulty)
            obj = instructor.objects.get(pk=request.session['instructorid'])
            instructorname = obj.uname
            args = {'user1': obj,
                    'instructorname': instructorname,
                    'questions': questions,
                    'difficulty':did,
                    'content':content,
                    'total':total,
                    'remaining':remaining
                    }
            return render(request, 'instructor/make_quiz1.html', args)
        else:
            lock='0'
            if request.POST.get('mode1') == "lock" :
                lock = '1'
            if request.POST.get('mode1') == "hide" :
                lock = '0'
            title = request.POST.get('title')
            content = coursecontent.objects.get(pk=request.POST.get('content'))
            desc = request.POST.get('desc')
            duration =request.POST.get('duration')
            weightage = request.POST.get('weightage')
            startdate = request.POST.get('startdate')
            question_list = request.POST.getlist('selected_questions')
            questions = add_question.objects.filter(id__in=question_list)
            list1 = list()
            for q in questions:
                list1.append(q.id)
            difficulty = request.POST.get('difficulty')
            did = difficulty_levels.objects.get(name=difficulty)
            quiz_obj = quiz(content_id=content,instructor_id=obj,question_id=list1,quiz_title=title,quiz_description=desc,quiz_duration=duration,quiz_weightage=weightage,quiz_date=startdate,difficulty=did,lock=lock,hide='0')
            quiz_obj.save()

            quiz_obj = quiz.objects.filter(instructor_id=obj.id)
            list1 = list()
            for q in quiz_obj:
                list1.append(q.content_id)


            instructorname = obj.uname
            args = {'user1': obj,
                    'instructorname': instructorname,
                    'quizs': quiz_obj
                    }

            return HttpResponseRedirect(reverse(quiz_display1,args=(content.course_id.id,)))
    else:
        return HttpResponseRedirect('/instructor/login/')

def quiz_display(request):
    if request.session.get('instructorid') != None:
        obj = instructor.objects.get(pk=request.session['instructorid'])
        quiz_obj = quiz.objects.filter(instructor_id=obj.id)

        #contentobj = coursecontent.objects.filter(course_id = quiz_obj.content_id)
        #print(contentobj)

        instructorname = obj.uname
        args = {'user1': obj,
                'instructorname': instructorname,
                'quizs': quiz_obj,
                }
        return render(request, 'instructor/quiz_display.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def quiz_display1(request,course_id):
    if request.session.get('instructorid') != None:
        obj = instructor.objects.get(pk=request.session['instructorid'])
        quizs = quiz.objects.filter(instructor_id=obj.id)
        quiz_obj = list()
        for quiz1 in quizs:
            if quiz1.content_id.course_id.id == int(course_id):
                quiz_obj.append(quiz1)

        courseid = course.objects.get(pk=course_id)
        contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by(
                'content_sequence_no')
        difficulty_obj = difficulty_levels.objects.all()

        instructorname = obj.uname
        args = {'user1': obj,
                'instructorname': instructorname,
                'quizs': quiz_obj,
                'course_id':course_id,
                'content': contentobj,
                'difficulty':difficulty_obj
                }
        return render(request, 'instructor/quiz_display.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def quiz_details(request,quiz_id):
    if request.session.get('instructorid') != None:
        obj = instructor.objects.get(pk=request.session['instructorid'])
        quiz_obj = quiz.objects.get(pk=quiz_id)
        list1 = quiz_obj.question_id
        list2 = str(list1)[1:-1]
        ids = list2.split(",")
        ids = [x.strip(' ') for x in ids]
        questions = add_question.objects.filter(id__in=ids)

        instructorname = obj.uname
        args = {'user1': obj,
                'instructorname': instructorname,
                'quiz': quiz_obj,
                'questions': questions
                }
        return render(request, 'instructor/quiz_details.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def edit_quiz(request,quiz_id):
    if request.session.get('instructorid') != None:
        if request.method == 'POST':
            obj = instructor.objects.get(pk=request.session['instructorid'])
            quiz_obj = quiz.objects.get(pk=quiz_id)
            quiz_obj.quiz_title = request.POST.get('title')
            quiz_obj.quiz_description = request.POST.get('desc')
            quiz_obj.quiz_duration = request.POST.get('duration')
            quiz_obj.save()
            quiz_obj = quiz.objects.get(pk=quiz_id)
            list1 = quiz_obj.question_id
            list2 = str(list1)[1:-1]
            ids = list2.split(",")
            ids = [x.strip(' ') for x in ids]
            questions = add_question.objects.filter(id__in=ids)

            instructorname = obj.uname
            args = {'user1': obj,
                    'instructorname': instructorname,
                    'quiz': quiz_obj,
                    'questions': questions
                    }
            return HttpResponseRedirect(reverse(quiz_details,args=(quiz_id,)))
            #return render(request, 'instructor/quiz_details.html', args)
        else:
            obj = instructor.objects.get(pk=request.session['instructorid'])
            quiz_obj = quiz.objects.get(pk=quiz_id)
            difficulty_obj = difficulty_levels.objects.all()
            quiz_obj1 = quiz.objects.filter(content_id=quiz_obj.content_id,lock='1')
            total=0
            for q in quiz_obj1:
                total = total + int(q.quiz_weightage)
            remaining = 100 - total
            instructorname = obj.uname
            args = {'user1': obj,
                    'instructorname': instructorname,
                    'quiz': quiz_obj,
                    'difficulty': difficulty_obj,
                    'total':total,
                    'remaining':remaining
                    }
            return render(request, 'instructor/edit_quiz.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def edit_quiz1(request,quiz_id):
    if request.session.get('instructorid') != None:
        if request.method == 'POST':
            obj = instructor.objects.get(pk=request.session['instructorid'])
            quiz_obj = quiz.objects.get(pk=quiz_id)
            question_list = request.POST.getlist('selected_questions')
            questions = add_question.objects.filter(id__in=question_list)
            list1 = list()
            for q in questions:
                list1.append(q.id)
            quiz_obj.question_id = list1
            quiz_obj.save()
            quiz_obj = quiz.objects.get(pk=quiz_id)
            list1 = quiz_obj.question_id
            list2 = str(list1)[1:-1]
            ids = list2.split(",")
            ids = [x.strip(' ') for x in ids]
            questions = add_question.objects.filter(id__in=ids)
            instructorname = obj.uname
            args = {'user1': obj,
                    'instructorname': instructorname,
                    'quiz': quiz_obj,
                    'questions': questions
                    }
            return HttpResponseRedirect(reverse(quiz_details,args=(quiz_id,)))
            #return render(request, 'instructor/quiz_details.html', args)
        else:
            quiz_obj = quiz.objects.get(pk=quiz_id)
            obj = instructor.objects.get(pk=request.session['instructorid'])
            list1 = quiz_obj.question_id
            list2 = str(list1)[1:-1]
            ids = list2.split(",")
            ids = [x.strip(' ') for x in ids]
            questions1 = add_question.objects.filter(id__in=ids)
            questions = add_question.objects.filter(course_id=quiz_obj.content_id.course_id.id,difficulty=quiz_obj.difficulty.id).exclude(id__in=ids)
            instructorname = obj.uname
            args = {'user1': obj,
                    'instructorname': instructorname,
                    'questions': questions,
                    'questions1':questions1,
                    'quiz':quiz_obj
                    }
            return render(request, 'instructor/edit_quiz1.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')


def delete_quiz(request,quiz_id):
    if request.session.get('instructorid') != None:
        obj = instructor.objects.get(pk=request.session['instructorid'])
        quiz_obj = quiz.objects.get(pk=quiz_id)

        try:

            enroll_data = enrolldata.objects.filter(course_id=course.objects.get(pk=quiz_obj.content_id.course_id.id))

            a = []
            for edata in enroll_data:
                a.append(edata.student_id.id)
            for ids in set(a):
                try:
                    student_data = enrolldata.objects.get(student_id=student.objects.get(pk=ids),
                                                          course_id=course.objects.get(
                                                              pk=quiz_obj.content_id.course_id.id))
                    given_quizes = student_data.progress_data.split(',')

                    for gquiz in given_quizes:
                        if gquiz == quiz_obj.quiz_title:

                            try:
                                n = []
                                submission_data = submissions.objects.filter(student_id=student.objects.get(pk=ids),
                                                                             quiz_id=quiz_obj)
                                for sub_data in submission_data:
                                    n.append(sub_data.percentage)
                                max_percentage = max(n)
                                reduce_precentage = (float(quiz_obj.quiz_weightage) * float(max_percentage)) / 100
                                enrolldata.objects.filter(student_id=student.objects.get(pk=ids),
                                                          course_id=course.objects.get(
                                                              pk=quiz_obj.content_id.course_id.id)).update(
                                    course_progress=float(student_data.course_progress) - reduce_precentage,
                                    progress_data=student_data.progress_data.replace(quiz_obj.quiz_title + ',', '')
                                )
                            except:
                                # print('inner1')
                                None
                except:
                    # print('inner2')
                    None

        except:
            # print('except')
            None

        quiz_obj.delete()

        quiz_obj = quiz.objects.filter(instructor_id=obj.id)

        instructorname = obj.uname
        args = {'user1': obj,
                'instructorname': instructorname,
                'quizs': quiz_obj,
                }
        return HttpResponseRedirect(reverse(quiz_display))
        # return render(request, 'instructor/quiz_display.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')


def lock_quiz(request,quiz_id):
    if request.session.get('instructorid') != None:
        obj = instructor.objects.get(pk=request.session['instructorid'])
        quiz_obj = quiz.objects.get(pk=quiz_id)
        quiz_obj.lock = '1'
        quiz_obj.save()
        quiz_obj = quiz.objects.filter(instructor_id=obj.id)

        instructorname = obj.uname
        args = {'user1': obj,
                'instructorname': instructorname,
                'quizs': quiz_obj,
                }
        return HttpResponseRedirect(reverse(quiz_display))
        #return render(request, 'instructor/quiz_display.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def hide_quiz(request,quiz_id):
    if request.session.get('instructorid') != None:
        obj = instructor.objects.get(pk=request.session['instructorid'])
        quiz_obj = quiz.objects.get(pk=quiz_id)
        if quiz_obj.hide == '1':
            quiz_obj.hide = 0
        else:
            quiz_obj.hide = 1
        quiz_obj.save()
        quiz_obj = quiz.objects.filter(instructor_id=obj.id)

        instructorname = obj.uname
        args = {'user1': obj,
                'instructorname': instructorname,
                'quizs': quiz_obj,
                }
        return HttpResponseRedirect(reverse(quiz_display))
        #return render(request, 'instructor/quiz_display.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def earnings(request):
    if request.session.get('instructorid') != None:
        obj = instructor.objects.get(pk=request.session['instructorid'])
        enrolls = enrolldata.objects.all()
        courses = course.objects.filter(creatorid=obj.id)
        cwise = list()
        total=0

        flag=0
        for c in courses:
            fee=c.fee
            flag=0
            individual=0
            for e in enrolls:
                if e.fee_status !='n' and e.course_id.id == c.id:
                    flag=1
                    individual = individual + fee
                    total = total + fee
            if flag == 1:
                cwise.append(individual)
            else:
                cwise.append(0)
        instructorname = obj.uname
        args = {'user1': obj,
                'instructorname': instructorname,
                'total': total,
                'course_wise':zip(courses,cwise)
                }
        return render(request, 'instructor/earnings.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def students_enrolled(request,course_id):
    if request.session.get('instructorid') != None:
        enrolls = enrolldata.objects.filter(course_id=course_id)
        obj = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = obj.uname
        args = {'user1': obj,
                'instructorname': instructorname,
                'enrolls': enrolls,
                'id':course_id
                }
        return render(request, 'instructor/students_enrolled.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def managereview(request):
    course_data=course.objects.filter(creatorid=instructor.objects.get(pk=request.session.get('instructorid')))
    review_data=review.objects.all().order_by('flag')
    return render(request,'instructor/managereview.html',{'reviews':review_data,'courses':course_data})

@csrf_exempt
def approve(request,review_id):
    review.objects.filter(pk=review_id).update(flag='y')
    course_data = course.objects.filter(creatorid=instructor.objects.get(pk=request.session.get('instructorid')))
    review_data = review.objects.all().order_by('flag')
    return render(request, 'instructor/refresh_review.html', {'reviews': review_data, 'courses': course_data})

@csrf_exempt
def remove(request,review_id):
    review.objects.filter(pk=review_id).update(flag='n')
    course_data = course.objects.filter(creatorid=instructor.objects.get(pk=request.session.get('instructorid')))
    review_data = review.objects.all().order_by('flag')
    for r in review_data:
        print(r.flag)
    return render(request, 'instructor/refresh_review.html', {'reviews': review_data, 'courses': course_data})

def sendmail(request,course_id):
    udata=enrolldata.objects.filter(course_id=course.objects.get(pk=1))
    subject = request.POST.get('subject')
    print(subject)
    description = request.POST.get('desc')
    print(description)
    for u in udata:
        send_mail(
            subject,
            description,
            'harshitus99@gmail.com',
            [u.student_id.email],
            fail_silently=False,
        )
    enrolls = enrolldata.objects.filter(course_id=course_id)
    obj = instructor.objects.get(pk=request.session['instructorid'])
    instructorname = obj.uname
    args = {'user1': obj,
                'instructorname': instructorname,
                'enrolls': enrolls
                }
    return render(request,'instructor/students_enrolled.html',args)



def upload_csv(request,course_id):

    if request.FILES:
        upload = request.FILES['content_file']
        data = uploadcsv(csvfile=upload)
        data.save()

        course_obj = course.objects.get(id=course_id)
        ifile = open(settings.MEDIA_ROOT + "/" + str(data.csvfile), "r")
        read = csv.reader(ifile)
        for row in read:
            quiestion_daata = add_question.objects.filter(course_id=course_obj)
            try:
                d = add_question.objects.get(question=row[0])
            except:
                if row[10] == "1":
                    question_obj = add_question(question_type='0', course_id=course_obj, question=row[0], answer=row[5],
                                        feedbackc=row[6],
                                        feedbackw=row[7], hint=row[8],
                                        difficulty=difficulty_levels.objects.get(pk=int(row[9])),
                                        option1=row[1], option2=row[2], option3=row[3], option4=row[4])
                    question_obj.save()
                elif row[10] == "2":
                    question_obj = add_question(question_type='1', course_id=course_obj, question=row[0], answer=row[5],
                                        feedbackc=row[6],
                                        feedbackw=row[7], hint=row[8],
                                        difficulty=difficulty_levels.objects.get(pk=int(row[9]))
                                        )
                    question_obj.save()
                elif row[10] == "3":
                    question_obj = add_question(question_type='2', course_id=course_obj, question=row[0], answer=row[5],
                                        feedbackc=row[6],
                                        feedbackw=row[7], hint=row[8],
                                        difficulty=difficulty_levels.objects.get(pk=int(row[9]))
                                        )
                    question_obj.save()
    return HttpResponseRedirect(reverse(question_bank1,args=(course_id,)))
    #return render(request, 'instructor/question_bank.html', args)

def faqs(request):
    if request.session.get('instructorid') != None:
        form=faq_Form()
        if request.method == 'POST':
            question = request.POST.get('question')
            answer = request.POST.get('faq_answer')
            if request.POST.get('faq_answer') == "":
                obj = instructor.objects.get(pk=request.session['instructorid'])
                courses = course.objects.filter(creatorid=request.session['instructorid'])
                instructorname = obj.uname
                args = {'user1': obj,
                        'form':form,
                        'courses': courses,
                        'instructorname': instructorname,
                        'mode':'error',
                        'question':question}
                return render(request, 'instructor/faq.html', args)
            else:
                course_id = request.POST.get('courses')
                data = course.objects.get(pk=course_id)
                faq_obj=faq(faq_question= question,faq_answer=answer,course_id=data)
                faq_obj.save()
                obj = instructor.objects.get(pk=request.session['instructorid'])
                instructorname = obj.uname
                return HttpResponseRedirect(reverse(instructor_panel))
            #return render(request, 'instructor/instructor_panel.html', args)
        else:
            obj = instructor.objects.get(pk=request.session['instructorid'])
            courses = course.objects.filter(creatorid=request.session['instructorid'])
            instructorname = obj.uname
            args = {'user1': obj,
                    'form':form,
                    'courses': courses,
                    'instructorname': instructorname,
                    'mode':'first_time',
                    'question':""}
            return render(request, 'instructor/faq.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def faq_display(request,course_id):
    if request.session.get('instructorid') != None:
        faq_obj = faq.objects.filter(course_id=course_id)
        form=faq_Form()
        obj = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = obj.uname
        args = {'user1': obj,
                'form':form,
                'instructorname': instructorname,
                'faqs':faq_obj,
                'course_id':course_id}
        return render(request, 'instructor/faq_display.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')

def delete_faq(request,faq_id):
    if request.session.get('instructorid') != None:
        faq_obj = faq.objects.get(id=faq_id)
        course_id = faq_obj.course_id.id
        faq_obj.delete()
        faq_obj = faq.objects.filter(course_id=course_id)
        form=faq_Form()
        obj = instructor.objects.get(pk=request.session['instructorid'])
        instructorname = obj.uname
        return HttpResponseRedirect(reverse(faq_display,args=(course_id,)))
        #return render(request, 'instructor/faq_display.html', args)
    else:
        return HttpResponseRedirect('/instructor/login/')
