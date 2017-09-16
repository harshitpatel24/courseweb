import datetime
import random

from django.core.serializers import json
from django.db.models import Max
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas

from coursewebsite.settings import MEDIA_ROOT
from forum.models import Forum
from instructor.models import course, enrolldata, coursecontent, announcements, quiz, add_question, faq, resources1
from joinus.models import student
from course.models import review, submissions, course_progress, certificate
import itertools
from coursewebsite import settings

def course_overview(request):
    courses = course.objects.all().exclude(lock='0')
    try:
        enroll1 = enrolldata.objects.filter(student_id=student.objects.get(pk=request.session.get('userid'))).order_by(
        'course_id__id')
    except:
        enroll1=''
    if 'userid' in request.session:
        obj = student.objects.get(pk=request.session['userid'])
        username = obj.uname
        nav = 'logout'
        try:
            a = []
            for c in courses:
                global rating
                rating=0
                global count
                count=0
                try:
                    cdata = review.objects.filter(course_id=course.objects.get(pk=c.id)).exclude(flag='n')
                    for c1 in cdata:
                        if c1.course_id.id == c.id:
                           count = count + 1
                           rating = float(rating) + float(c1.rating)
                    a.append(c.cname)
                    a.append(float( rating / count))
                except:
                    a.remove(c.cname)
                    a.append(c.cname)
                    a.append(0)
            d = dict(itertools.zip_longest(*[iter(a)] * 2, fillvalue=""))
        except:
            rating_data=None

    else:
        username = 'Guest,Plz Login'
        nav = 'register'
        try:
            a = []
            for c in courses:
                rating=0
                count=0
                try:
                    cdata = review.objects.filter(course_id=course.objects.get(pk=c.id)).exclude(flag='n')
                    for c1 in cdata:
                        if c1.course_id.id == c.id:
                           count = count + 1
                           rating = float(rating) + float(c1.rating)
                    a.append(c.cname)
                    a.append(float( rating / count))
                except:
                    a.remove(c.cname)
                    a.append(c.cname)
                    a.append(0)
            d = dict(itertools.zip_longest(*[iter(a)] * 2, fillvalue=""))
        except:
            rating_data=None
    return render(request, 'course/courses.html',
                  {'courses': courses, 'nav': nav, 'data': enroll1, 'username': username,'rating_data':d})

def view_course(request, course_id):
    try:
        findenroll=enrolldata.objects.get(course_id=course.objects.get(pk=course_id),student_id=student.objects.get(pk=request.session.get('userid')))
        try:
            faqlist = faq.objects.filter(course_id=course_id)
        except:
            faqlist=''
        if request.session.get('userid') != None:

            fee = ''
            flag = ''
            courseid = course.objects.get(pk=course_id)
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by(
                'content_sequence_no')
            contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0).order_by(
                'content_sequence_no')
            courseobj = course.objects.get(id=courseid.id)

            obj = student.objects.get(pk=request.session['userid'])
            username = obj.uname
            global review_user
            review_user = None
            try:
                review_course = review.objects.filter(course_id=course.objects.get(pk=course_id), flag='y')
            except:
                None
            try:
                review_user = review.objects.get(course_id=course.objects.get(pk=course_id),
                                                 student_id=student.objects.get(pk=request.session.get('userid')))
            except:
                None
            try:
                entry = enrolldata.objects.get(student_id=student.objects.get(pk=request.session.get('userid')),
                                               course_id=courseid)
                fee += entry.fee_status
                flag += entry.flag
            except Exception:
                course_data = course.objects.get(pk=course_id)
                data = enrolldata(student_id=student.objects.get(pk=request.session.get('userid')),
                                  course_id=course_data,
                                  join_date=str(datetime.datetime.now()), fee_status='n', course_progress='0', flag='0',
                                  progress_data='')
                data.save()
                fee += 'n'
                flag += '0'
            # print(coursecontent._meta.pk.name)
            try:
                announcement_data = announcements.objects.filter(course_id=course.objects.get(pk=course_id)).order_by(
                    '-pk')
            except:
                announcement_data = ''
            d = {}
            try:
                a = []
                cdata = coursecontent.objects.filter(course_id=course_id)
                for c in cdata:
                    try:
                        quiz_data = quiz.objects.filter(content_id=c.pk).exclude(hide=1)
                        for q in quiz_data:
                            a.append(q.quiz_title)
                            a.append(c.content_name)
                        d = dict(itertools.zip_longest(*[iter(a)] * 2, fillvalue=""))

                    except:
                        None
            except:
                d = {}
            try:
                forumobj = Forum.objects.get(courseid=courseid)
                forumlink = forumobj.pk
            except:
                forumlink = -1

            args = {
                'reviewuser': review_user,
                'reviews': review_course,
                'username': username,
                'course': courseobj,
                'content': contentobj,
                'subcontent': contentobj1,
                'fee': fee,
                'faqlist': faqlist,
                'flag': flag,
                'announcement_data': announcement_data,
                'course_quizes': d,
                'quizes': quiz.objects.all().exclude(hide=1),
                'forumid': forumlink
            }

            return render(request, 'course/full_course.html', args)

        else:
            return HttpResponseRedirect('/joinus/login/')


    except:
        courseid = course.objects.get(pk=course_id)
        faqlist = faq.objects.filter(course_id=course_id)
        contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by('content_sequence_no')
        contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0).order_by('content_sequence_no')
        courseobj = course.objects.get(id=courseid.id)
        try:
            review_course = review.objects.filter(course_id=course.objects.get(pk=course_id), flag='y')
        except:
            review_course=None
        try:
            forumobj = Forum.objects.get(courseid=courseid)
            forumlink = forumobj.pk

            if 'userid' in request.session:
                obj = student.objects.get(pk=request.session['userid'])
                username = obj.uname
                nav = 'logout'
            else:
                username = 'Guest,Plz Login'
                nav = 'register'
            try:
                user_data = student.objects.get(pk=request.session['userid'])
                entry = enrolldata.objects.get(student_id=user_data, course_id=course_id)
                args = {
                    'course': courseobj,
                    'content': contentobj,
                    'subcontent': contentobj1,
                    'nav': nav,
                    'faqlist': faqlist,
                    'reviews': review_course,
                    'message': 'Already Registered',
                    'username': username,
                    'forumid': forumlink,
                    'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                }
                return render(request, 'course/view_course.html', args)
            except:
                args = {
                    'course': courseobj,
                    'content': contentobj,
                    'subcontent': contentobj1,
                    'nav': nav,
                    'faqlist': faqlist,
                    'reviews': review_course,
                    'username': username,
                    'forumid': forumlink,
                    'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                }
                return render(request, 'course/view_course.html', args)
        except:

            if 'userid' in request.session:
                obj = student.objects.get(pk=request.session['userid'])
                username = obj.uname
                nav = 'logout'
            else:
                username = 'Guest,Plz Login'
                nav = 'register'
            try:
                user_data = student.objects.get(pk=request.session['userid'])
                entry = enrolldata.objects.get(student_id=user_data, course_id=course_id)
                args = {
                    'course': courseobj,
                    'content': contentobj,
                    'subcontent': contentobj1,
                    'nav': nav,
                    'faqlist': faqlist,
                    'reviews': review_course,
                    'message': 'Already Registered',
                    'username': username,
                    'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                }
                return render(request, 'course/view_course.html', args)
            except:
                args = {
                    'course': courseobj,
                    'content': contentobj,
                    'subcontent': contentobj1,
                    'nav': nav,
                    'faqlist': faqlist,
                    'reviews': review_course,
                    'username': username,

                    'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                }
                return render(request, 'course/view_course.html', args)

def enroll(request, course_id):
    if request.session.get('userid') != None:
        try:
            faqlist = faq.objects.filter(course_id=course_id)
        except:
            faqlist=''
        if request.method == 'POST':
            fee = ''
            flag = ''
            courseid = course.objects.get(pk=course_id)
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by('content_sequence_no')
            contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0).order_by('content_sequence_no')
            courseobj = course.objects.get(id=courseid.id)
            obj = student.objects.get(pk=request.session['userid'])
            username = obj.uname
            global review_user
            review_user = None
            try:
                review_course = review.objects.filter(course_id=course.objects.get(pk=course_id), flag='y')
            except:
                None
            try:
                review_user = review.objects.get(course_id=course.objects.get(pk=course_id),
                                                 student_id=student.objects.get(pk=request.session.get('userid')))
            except:
                None
            try:
                entry = enrolldata.objects.get(student_id=student.objects.get(pk=request.session.get('userid')),
                                               course_id=courseid)
                fee += entry.fee_status
                flag += entry.flag
            except Exception:
                course_data = course.objects.get(pk=course_id)
                data = enrolldata(student_id=student.objects.get(pk=request.session.get('userid')), course_id=course_data,
                                  join_date=str(datetime.datetime.now()), fee_status='n', course_progress='0', flag='0',
                                  progress_data='')
                data.save()
                fee += 'n'
                flag += '0'
            # print(coursecontent._meta.pk.name)
            try:
                announcement_data = announcements.objects.filter(course_id=course.objects.get(pk=course_id)).order_by('-pk')
            except:
                announcement_data = ''
            d = {}
            try:
                a = []
                cdata = coursecontent.objects.filter(course_id=course_id)
                for c in cdata:
                    try:
                        quiz_data = quiz.objects.filter(content_id=c.pk).exclude(hide=1)
                        for q in quiz_data:
                            a.append(q.quiz_title)
                            a.append(c.content_name)
                        d = dict(itertools.zip_longest(*[iter(a)] * 2, fillvalue=""))

                    except:
                        None
            except:
                d = {}
            try:
                forumobj = Forum.objects.get(courseid=courseid)
                forumlink = forumobj.pk
            except:
                forumlink = -1

            args = {
                'reviewuser': review_user,
                'reviews': review_course,
                'username': username,
                'course': courseobj,
                'content': contentobj,
                'subcontent': contentobj1,
                'fee': fee,
                'flag': flag,
                'faqlist':faqlist,
                'announcement_data': announcement_data,
                'course_quizes': d,
                'quizes': quiz.objects.all().exclude(hide=1),
                'forumid': forumlink
            }

            return render(request, 'course/full_course.html', args)
        else:
            try:
                find=enrolldata.objects.get(course_id=course.objects.get(pk=course_id),student_id=student.objects.get(pk=request.session.get('userid')))
                fee = ''
                flag = ''
                courseid = course.objects.get(pk=course_id)
                contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by(
                    'content_sequence_no')
                contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0).order_by(
                    'content_sequence_no')
                courseobj = course.objects.get(id=courseid.id)
                obj = student.objects.get(pk=request.session['userid'])
                username = obj.uname
                review_user = None
                try:
                    review_course = review.objects.filter(course_id=course.objects.get(pk=course_id), flag='y')
                except:
                    None
                try:
                    review_user = review.objects.get(course_id=course.objects.get(pk=course_id),
                                                     student_id=student.objects.get(pk=request.session.get('userid')))
                except:
                    None
                try:
                    entry = enrolldata.objects.get(student_id=student.objects.get(pk=request.session.get('userid')),
                                                   course_id=courseid)
                    fee += entry.fee_status
                    flag += entry.flag
                except Exception:
                    course_data = course.objects.get(pk=course_id)
                    fee += 'n'
                    flag += '0'
                # print(coursecontent._meta.pk.name)
                try:
                    announcement_data = announcements.objects.filter(
                        course_id=course.objects.get(pk=course_id)).order_by('-pk')
                except:
                    announcement_data = ''
                d = {}
                try:
                    a = []
                    cdata = coursecontent.objects.filter(course_id=course_id)
                    for c in cdata:
                        try:
                            quiz_data = quiz.objects.filter(content_id=c.pk).exclude(hide=1)
                            for q in quiz_data:
                                a.append(q.quiz_title)
                                a.append(c.content_name)
                            d = dict(itertools.zip_longest(*[iter(a)] * 2, fillvalue=""))

                        except:
                            None
                except:
                    d = {}
                try:
                    forumobj = Forum.objects.get(courseid=courseid)
                    forumlink = forumobj.pk
                except:
                    forumlink = -1

                args = {
                    'reviewuser': review_user,
                    'reviews': review_course,
                    'username': username,
                    'course': courseobj,
                    'content': contentobj,
                    'subcontent': contentobj1,
                    'fee': fee,
                    'flag': flag,
                    'faqlist':faqlist,
                    'announcement_data': announcement_data,
                    'course_quizes': d,
                    'quizes': quiz.objects.all().exclude(hide=1),
                    'forumid': forumlink
                }

                return render(request, 'course/full_course.html', args)
            except:
                courseid = course.objects.get(pk=course_id)
                faqlist = faq.objects.filter(course_id=course_id)
                contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by(
                    'content_sequence_no')
                contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0).order_by(
                    'content_sequence_no')
                courseobj = course.objects.get(id=courseid.id)
                try:
                    review_course = review.objects.filter(course_id=course.objects.get(pk=course_id), flag='y')
                except:
                    review_course = None
                try:
                    forumobj = Forum.objects.get(courseid=courseid)
                    forumlink = forumobj.pk

                    if 'userid' in request.session:
                        obj = student.objects.get(pk=request.session['userid'])
                        username = obj.uname
                        nav = 'logout'
                    else:
                        username = 'Guest,Plz Login'
                        nav = 'register'
                    try:
                        user_data = student.objects.get(pk=request.session['userid'])
                        entry = enrolldata.objects.get(student_id=user_data, course_id=course_id)
                        args = {
                            'course': courseobj,
                            'content': contentobj,
                            'subcontent': contentobj1,
                            'nav': nav,
                            'faqlist': faqlist,
                            'reviews': review_course,
                            'message': 'Already Registered',
                            'username': username,
                            'forumid': forumlink,
                            'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                        }
                        return render(request, 'course/view_course.html', args)
                    except:
                        args = {
                            'course': courseobj,
                            'content': contentobj,
                            'subcontent': contentobj1,
                            'nav': nav,
                            'faqlist': faqlist,
                            'reviews': review_course,
                            'username': username,
                            'forumid': forumlink,
                            'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                        }
                        return render(request, 'course/view_course.html', args)
                except:

                    if 'userid' in request.session:
                        obj = student.objects.get(pk=request.session['userid'])
                        username = obj.uname
                        nav = 'logout'
                    else:
                        username = 'Guest,Plz Login'
                        nav = 'register'
                    try:
                        user_data = student.objects.get(pk=request.session['userid'])
                        entry = enrolldata.objects.get(student_id=user_data, course_id=course_id)
                        args = {
                            'course': courseobj,
                            'content': contentobj,
                            'subcontent': contentobj1,
                            'nav': nav,
                            'faqlist': faqlist,
                            'reviews': review_course,
                            'message': 'Already Registered',
                            'username': username,
                            'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                        }
                        return render(request, 'course/view_course.html', args)
                    except:
                        args = {
                            'course': courseobj,
                            'content': contentobj,
                            'subcontent': contentobj1,
                            'nav': nav,
                            'faqlist': faqlist,
                            'reviews': review_course,
                            'username': username,

                            'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                        }
                        return render(request, 'course/view_course.html', args)



    else:
        return HttpResponseRedirect('/joinus/login/')

def payment(request, course_id):
    if request.session.get('userid') != None:
        enrolldata.objects.filter(student_id=student.objects.get(pk=request.session.get('userid')),
                                  course_id=course_id).update(fee_status='y')
        obj = student.objects.get(pk=request.session['userid'])
        username = obj.uname
        return HttpResponseRedirect(reverse('enroll', kwargs={'course_id': course_id}))
    else:
        return HttpResponseRedirect('/joinus/login/')

def continue_pay(request, course_id):
    if request.session.get('userid') != None:
        enrolldata.objects.filter(student_id=student.objects.get(pk=request.session.get('userid')),
                                  course_id=course_id).update(flag='1')
        obj = student.objects.get(pk=request.session['userid'])
        username = obj.uname
        return HttpResponseRedirect(reverse('enroll', kwargs={'course_id': course_id}))
    else:
        return HttpResponseRedirect('/joinus/login/')

def mycourse(request):
    if request.session.get('userid') != None:
        try:
            entry = enrolldata.objects.filter(student_id=student.objects.get(pk=request.session.get('userid')))
            obj = student.objects.get(pk=request.session['userid'])
            username = obj.uname
        except:
            entry = None
            username = 'Guest,Plz Login'
        return render(request, 'student/enrolled_student.html', {'courses': entry, 'username': username})
    else:
        return HttpResponseRedirect('/joinus/login/')

def review1(request, course_id):
    if request.session.get('userid') != None:
        if request.method == 'POST':
            rating = request.POST.get('input-21b')
            review1 = request.POST.get('review')
            obj = student.objects.get(pk=request.session['userid'])
            username = obj.uname
            try:
                data = review.objects.all()
                global flag1
                flag1 = 0
                for d in data:
                    if d.course_id == course.objects.get(pk=course_id) and d.student_id == student.objects.get(
                            pk=request.session.get('userid')):
                        review.objects.filter(course_id=course.objects.get(pk=course_id),
                                              student_id=student.objects.get(pk=request.session.get('userid'))).update(
                            rating=rating, review=review1, flag='n')
                        flag1 = 1
                        break
                    else:
                        flag1 = 0
                if flag1 == 0:
                    data = review(student_id=student.objects.get(pk=request.session.get('userid')),
                                  course_id=course.objects.get(pk=course_id), rating=rating, review=review1,
                                  status='active', flag='n')
                    data.save()
            except:
                None
        return HttpResponseRedirect(reverse('enroll', kwargs={'course_id': course_id}))
    else:
        return HttpResponseRedirect('/joinus/login/')


def course_review(request, course_id):
    if request.session.get('userid') != None:
        coursedata = course.objects.get(pk=course_id)
        try:
            reviewdata = review.objects.filter(course_id=course.objects.get(pk=course_id), flag='y').exclude(
                student_id=student.objects.get(pk=request.session.get('userid')))
        except:
            reviewdata=None
        obj = student.objects.get(pk=request.session['userid'])
        username = obj.uname
        try:
            userreview = review.objects.get(course_id=course.objects.get(pk=course_id),
                                            student_id=student.objects.get(pk=request.session.get('userid')))
        except:
            userreview = None
        contentobj = coursecontent.objects.filter(course_id=coursedata, content_sub_id=0)
        return render(request, 'course/review.html',
                      {'course': coursedata, 'reviews': reviewdata, 'username': username, 'content': contentobj,
                       'userreview': userreview})
    else:
        return HttpResponseRedirect('/joinus/login/')

def contentdisplay(request, course_name, content_id):
    if request.session.get('userid') != None:
        data = coursecontent.objects.get(pk=content_id)
        coursedata = course.objects.get(cname=course_name)
        obj = student.objects.get(pk=request.session['userid'])
        username = obj.uname
        contents = coursecontent.objects.filter(content_sub_id=content_id)
        try:
            reviewuser = review.objects.get(course_id=course.objects.get(pk=coursedata.id),
                                        student_id=student.objects.get(pk=request.session.get('userid')))
        except:
            reviewuser = None
        return render(request, 'course/contentdisplay.html',
                      {'data': data, 'username': username, 'course': coursedata, 'contents': contents,
                       'reviewuser': reviewuser})
    else:
        return HttpResponseRedirect('/joinus/login/')

def videodisplay(request, content_id, number):
    if request.session.get('userid') != None:
        try:
            coursedata = coursecontent.objects.get(pk=content_id)
            find = enrolldata.objects.get(course_id=course.objects.get(pk=coursedata.course_id.id),
                                          student_id=student.objects.get(pk=request.session.get('userid')))
            data = coursecontent.objects.get(pk=content_id)
            try:
                resources_data = resources1.objects.filter(content_id=coursecontent.objects.get(pk=content_id)).order_by(
                    'sequence_no')
                # file=open(MEDIA_ROOT+re)
            except:
                resources_data = ''
            if number == '0':
                show_data = data
                file_data = ''
            else:
                show_data = resources1.objects.get(pk=int(number))
                try:
                    file_data = ''
                    file = open(settings.MEDIA_ROOT + "/" + str(show_data.content_url1), "r")
                    content = [line.strip() for line in file]
                    for i in content:
                        file_data += str(i) + '\n'

                except:

                    file_data = ''
            obj = student.objects.get(pk=request.session['userid'])
            username = obj.uname
            try:
                maincontent = coursecontent.objects.get(pk=data.content_sub_id)
            except:
                maincontent = None
            try:
                prev = coursecontent.objects.get(content_sequence_no=data.content_sequence_no - 1,
                                                 content_sub_id=maincontent.pk)
            except:
                prev = -1
            try:
                next1 = coursecontent.objects.get(content_sequence_no=data.content_sequence_no + 1,
                                                  content_sub_id=maincontent.pk)
            except:
                next1 = -1
            try:
                reviewuser = review.objects.get(course_id=course.objects.get(pk=data.course_id.id),
                                                student_id=student.objects.get(pk=request.session.get('userid')))
            except:
                reviewuser = None

            return render(request, 'course/video.html',
                          {'data': data, 'maincontent': maincontent, 'username': username, 'prev': prev, 'next1': next1,
                           'reviewuser': reviewuser, 'course': course.objects.get(pk=data.course_id.id),
                           'resource_data': resources_data, 'show_data': show_data, 'number': number,
                           'file_data': file_data})
        except:
            coursedata=coursecontent.objects.get(pk=content_id)
            course_id=coursedata.course_id.id
            courseid = course.objects.get(pk=course_id)
            faqlist = faq.objects.filter(course_id=course_id)
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by(
                'content_sequence_no')
            contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0).order_by(
                'content_sequence_no')
            courseobj = course.objects.get(id=courseid.id)
            try:
                review_course = review.objects.filter(course_id=course.objects.get(pk=course_id), flag='y')
            except:
                review_course = None
            try:
                forumobj = Forum.objects.get(courseid=courseid)
                forumlink = forumobj.pk

                if 'userid' in request.session:
                    obj = student.objects.get(pk=request.session['userid'])
                    username = obj.uname
                    nav = 'logout'
                else:
                    username = 'Guest,Plz Login'
                    nav = 'register'
                try:
                    user_data = student.objects.get(pk=request.session['userid'])
                    entry = enrolldata.objects.get(student_id=user_data, course_id=course_id)
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'message': 'Already Registered',
                        'username': username,
                        'forumid': forumlink,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
                except:
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'username': username,
                        'forumid': forumlink,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
            except:

                if 'userid' in request.session:
                    obj = student.objects.get(pk=request.session['userid'])
                    username = obj.uname
                    nav = 'logout'
                else:
                    username = 'Guest,Plz Login'
                    nav = 'register'
                try:
                    user_data = student.objects.get(pk=request.session['userid'])
                    entry = enrolldata.objects.get(student_id=user_data, course_id=course_id)
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'message': 'Already Registered',
                        'username': username,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
                except:
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'username': username,

                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)


    else:
        return HttpResponseRedirect('/joinus/login/')

@csrf_exempt
def unenroll(request):
    if request.session.get('userid') != None:
        course_id=int(request.POST.get('course_id'))
        try:
            data1 = review.objects.get(course_id=course.objects.get(pk=course_id),
                                       student_id=student.objects.get(pk=request.session.get('userid')))
            data1.status = 'unenrolled'
            data1.save()
        except:
            None
        try:
            data = enrolldata.objects.get(course_id=course.objects.get(pk=course_id),
                                      student_id=student.objects.get(pk=request.session.get('userid')))
            data.delete()
        except:
            None
        try:
            entry = enrolldata.objects.filter(student_id=student.objects.get(pk=request.session.get('userid')))
            obj = student.objects.get(pk=request.session['userid'])
            username = obj.uname
        except:
            entry = None
            username = 'Guest,Plz Login'
        try:
            enroll_data = enrolldata.objects.filter(
                student_id=student.objects.get(pk=request.session.get('userid'))).exclude(course_progress='100.0')
        except:
            enroll_data = ''
        try:
            completed_data = enrolldata.objects.filter(course_progress='100.0',
                                                       student_id=student.objects.get(pk=request.session.get('userid')))
        except:
            completed_data = ''
        return render(request, 'student/enrolled_student.html', {'courses': enroll_data,'username':student.objects.get(pk=request.session.get('userid')),'completed':completed_data})

    else:
        return HttpResponseRedirect('/joinus/login/')

def all_announcement(request, course_id):
    if request.session.get('userid') != None:
        try:
            find=enrolldata.objects.get(course_id=course.objects.get(pk=course_id),student_id=student.objects.get(pk=request.session.get('userid')))

            announcement_data = announcements.objects.filter(course_id=course.objects.get(pk=course_id)).order_by('-pk')
            courseid = course.objects.get(pk=course_id)
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0)
            courseobj = course.objects.get(id=courseid.id)
            username = student.objects.get(pk=request.session.get('userid'))
            try:
                review_user = review.objects.get(course_id=course.objects.get(pk=course_id),
                                             student_id=student.objects.get(pk=request.session.get('userid')))
            except:
                review_user=None
            return render(request, 'course/announcement.html', {'username': username,
                                                                'course': courseobj,
                                                                'content': contentobj,
                                                                'announcement_data': announcement_data,
                                                                'reviewuser': review_user
                                                                })
        except:
            courseid = course.objects.get(pk=course_id)
            faqlist = faq.objects.filter(course_id=course_id)
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by(
                'content_sequence_no')
            contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0).order_by(
                'content_sequence_no')
            courseobj = course.objects.get(id=courseid.id)
            try:
                review_course = review.objects.filter(course_id=course.objects.get(pk=course_id), flag='y')
            except:
                review_course = None
            try:
                forumobj = Forum.objects.get(courseid=courseid)
                forumlink = forumobj.pk

                if 'userid' in request.session:
                    obj = student.objects.get(pk=request.session['userid'])
                    username = obj.uname
                    nav = 'logout'
                else:
                    username = 'Guest,Plz Login'
                    nav = 'register'
                try:
                    user_data = student.objects.get(pk=request.session['userid'])
                    entry = enrolldata.objects.get(student_id=user_data, course_id=course_id)
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'message': 'Already Registered',
                        'username': username,
                        'forumid': forumlink,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
                except:
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'username': username,
                        'forumid': forumlink,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
            except:

                if 'userid' in request.session:
                    obj = student.objects.get(pk=request.session['userid'])
                    username = obj.uname
                    nav = 'logout'
                else:
                    username = 'Guest,Plz Login'
                    nav = 'register'
                try:
                    user_data = student.objects.get(pk=request.session['userid'])
                    entry = enrolldata.objects.get(student_id=user_data, course_id=course_id)
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'message': 'Already Registered',
                        'username': username,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
                except:
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'username': username,

                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)

    else:
        return HttpResponseRedirect('/joinus/login/')

def quiz1(request, course_id, quiz_name):
    if request.session.get('userid') != None:
        try:
            find = enrolldata.objects.get(course_id=course.objects.get(pk=course_id),
                                          student_id=student.objects.get(pk=request.session.get('userid')))
            courseid = course.objects.get(pk=course_id)
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0)
            courseobj = course.objects.get(id=courseid.id)
            username = student.objects.get(pk=request.session.get('userid'))
            try:
                review_user = review.objects.get(course_id=course.objects.get(pk=course_id),
                                             student_id=student.objects.get(pk=request.session.get('userid')))
            except:
                review_user=None
            quiz_data = quiz.objects.get(content_id__course_id=course_id, quiz_title=quiz_name)
            no_of_que = quiz_data.question_id[1:len(quiz_data.question_id) - 1].split(",")
            a = []
            for n in no_of_que:
                a.append(n.strip())
            return render(request, 'course/quiz.html', {'username': username,
                                                        'course': courseobj,
                                                        'content': contentobj,
                                                        'quiz_data': quiz_data,
                                                        'reviewuser': review_user,
                                                        'noofque': len(a)
                                                        })
        except:
            courseid = course.objects.get(pk=course_id)
            faqlist = faq.objects.filter(course_id=course_id)
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by(
                'content_sequence_no')
            contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0).order_by(
                'content_sequence_no')
            courseobj = course.objects.get(id=courseid.id)
            try:
                review_course = review.objects.filter(course_id=course.objects.get(pk=course_id), flag='y')
            except:
                review_course = None
            try:
                forumobj = Forum.objects.get(courseid=courseid)
                forumlink = forumobj.pk

                if 'userid' in request.session:
                    obj = student.objects.get(pk=request.session['userid'])
                    username = obj.uname
                    nav = 'logout'
                else:
                    username = 'Guest,Plz Login'
                    nav = 'register'
                try:
                    user_data = student.objects.get(pk=request.session['userid'])
                    entry = enrolldata.objects.get(student_id=user_data, course_id=course_id)
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'message': 'Already Registered',
                        'username': username,
                        'forumid': forumlink,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
                except:
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'username': username,
                        'forumid': forumlink,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
            except:

                if 'userid' in request.session:
                    obj = student.objects.get(pk=request.session['userid'])
                    username = obj.uname
                    nav = 'logout'
                else:
                    username = 'Guest,Plz Login'
                    nav = 'register'
                try:
                    user_data = student.objects.get(pk=request.session['userid'])
                    entry = enrolldata.objects.get(student_id=user_data, course_id=course_id)
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'message': 'Already Registered',
                        'username': username,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
                except:
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'username': username,

                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)

    else:
        return HttpResponseRedirect('/joinus/login/')

def start_quiz(request, quiz_id):

    if request.session.get('userid') != None:
        try:
            quiz_data = quiz.objects.get(pk=quiz_id)
            courseid = course.objects.get(pk=quiz_data.content_id.course_id.id)
            find = enrolldata.objects.get(course_id=course.objects.get(pk=courseid.id),
                                          student_id=student.objects.get(pk=request.session.get('userid')))
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0)
            courseobj = course.objects.get(id=courseid.id)
            username = student.objects.get(pk=request.session.get('userid'))
            try:
                review_user = review.objects.get(course_id=course.objects.get(pk=quiz_data.content_id.course_id.id),
                                             student_id=student.objects.get(pk=request.session.get('userid')))
            except:
                review_user=None
            no_of_que = quiz_data.question_id[1:len(quiz_data.question_id) - 1].split(",")
            a = []
            for n in no_of_que:
                a.append(int(n))
                a.append(quiz_data.id)
            d = dict(itertools.zip_longest(*[iter(a)] * 2, fillvalue=""))
            question_bank = add_question.objects.filter(course_id=courseid.id)
            return render(request, 'course/start_quiz.html',
                          {'username': username, 'course': courseobj, 'content': contentobj, 'quiz_data': quiz_data,
                           'questions': d, 'qbank': question_bank, 'reviewuser': review_user})

        except:
            quiz_data = quiz.objects.get(pk=quiz_id)
            courseid = course.objects.get(pk=quiz_data.content_id.course_id.id)
            course_id=courseid.id
            faqlist = faq.objects.filter(course_id=courseid)
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by(
                'content_sequence_no')
            contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0).order_by(
                'content_sequence_no')
            courseobj = course.objects.get(id=courseid.id)
            try:
                review_course = review.objects.filter(course_id=course.objects.get(pk=course_id), flag='y')
            except:
                review_course = None
            try:
                forumobj = Forum.objects.get(courseid=courseid)
                forumlink = forumobj.pk

                if 'userid' in request.session:
                    obj = student.objects.get(pk=request.session['userid'])
                    username = obj.uname
                    nav = 'logout'
                else:
                    username = 'Guest,Plz Login'
                    nav = 'register'
                try:
                    user_data = student.objects.get(pk=request.session['userid'])
                    entry = enrolldata.objects.get(student_id=user_data, course_id=course_id)
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'message': 'Already Registered',
                        'username': username,
                        'forumid': forumlink,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
                except:
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'username': username,
                        'forumid': forumlink,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
            except:

                if 'userid' in request.session:
                    obj = student.objects.get(pk=request.session['userid'])
                    username = obj.uname
                    nav = 'logout'
                else:
                    username = 'Guest,Plz Login'
                    nav = 'register'
                try:
                    user_data = student.objects.get(pk=request.session['userid'])
                    entry = enrolldata.objects.get(student_id=user_data, course_id=course_id)
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'message': 'Already Registered',
                        'username': username,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
                except:
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'username': username,

                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)




    else:
        return HttpResponseRedirect('/joinus/login/')

def submit_quiz(request, quiz_id):
    if request.session.get('userid') != None:
        try:
            quiz_data = quiz.objects.get(pk=quiz_id)
            courseid = course.objects.get(pk=quiz_data.content_id.course_id.id)
            find = enrolldata.objects.get(course_id=courseid,
                                          student_id=student.objects.get(pk=request.session.get('userid')))
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0)
            courseobj = course.objects.get(id=courseid.id)
            username = student.objects.get(pk=request.session.get('userid'))
            try:
                review_user = review.objects.get(course_id=course.objects.get(pk=quiz_data.content_id.course_id.id),
                                                 student_id=student.objects.get(pk=request.session.get('userid')))
            except:
                review_user = None
            no_of_que = quiz_data.question_id[1:len(quiz_data.question_id) - 1].split(",")
            total = len(no_of_que)
            global correct
            correct = 0
            answers_by_student = []
            right_answers = []
            if request.method == 'POST':

                for n in no_of_que:
                    questions = add_question.objects.get(pk=n.strip())
                    if questions.question_type == '0':

                        # answers_by_student.append(n.strip())
                        # answers_by_student.append(request.POST.get('radio_option' + n.strip()))
                        if questions.answer == 'a':
                            right_answers.append(n.strip())
                            right_answers.append(questions.option1)
                            try:
                                if request.POST.get('radio_option' + n.strip()) == questions.option1:
                                    correct += 1
                            except:
                                None
                        elif questions.answer == 'b':
                            right_answers.append(n.strip())
                            right_answers.append(questions.option2)
                            try:
                                if request.POST.get('radio_option' + n.strip()) == questions.option2:
                                    correct += 1
                            except:
                                None
                        elif questions.answer == 'c':
                            right_answers.append(n.strip())
                            right_answers.append(questions.option3)
                            try:
                                if request.POST.get('radio_option' + n.strip()) == questions.option3:
                                    correct += 1
                            except:
                                None
                        elif questions.answer == 'd':
                            right_answers.append(n.strip())
                            right_answers.append(questions.option4)
                            try:
                                if request.POST.get('radio_option' + n.strip()) == questions.option4:
                                    correct += 1
                            except:
                                None
                    if questions.question_type == '2':
                        data = questions.answer.split(",")
                        try:
                            answers = request.POST.getlist('checkbox_option' + n.strip())
                            # answers_by_student.append(n.strip())
                            # answers_by_student.append(answers)

                            c = []
                            for i in range(len(data)):
                                if data[i] == 'a':
                                    c.append(questions.option1)
                                if data[i] == 'b':
                                    c.append(questions.option2)
                                if data[i] == 'c':
                                    c.append(questions.option3)
                                if data[i] == 'd':
                                    c.append(questions.option4)
                            global count
                            count = 0
                            for a in answers:
                                for i in range(len(c)):
                                    if a == c[i]:
                                        count = count + 1
                            if count == len(c):
                                correct = correct + 1
                        except:
                            None
                    if questions.question_type == '1':
                        try:
                            ans = request.POST.get('single_answer' + n.strip())
                            answers_by_student.append(n.strip())
                            answers_by_student.append(ans)
                            if ans == questions.answer:
                                correct = correct + 1
                        except:
                            None

                p = (correct / total) * 100
                percentage = "%.2f" % round(p, 1)
                d = dict(itertools.zip_longest(*[iter(answers_by_student)] * 2, fillvalue=""))

                store = submissions(quiz_id=quiz.objects.get(pk=quiz_id),
                                    student_id=student.objects.get(pk=request.session.get('userid')), percentage=percentage,
                                    no_of_questions=total, submission_date=str(datetime.datetime.now().strftime("%d/%m/%Y")),
                                    submission_time=str(datetime.datetime.now().strftime("%H:%M")))
                store.save()
                submission_data = submissions.objects.get(pk=store.id)
                data = submissions.objects.filter(quiz_id=quiz.objects.get(pk=quiz_id),
                                                  student_id=student.objects.get(pk=request.session.get('userid')))
                d1 = submissions.objects.filter(quiz_id=quiz.objects.get(pk=quiz_id),
                                                student_id=student.objects.get(pk=request.session.get('userid'))).exclude(
                    pk=store.id)
                a = [0]
                for dd in d1:
                    a.append(dd.percentage)

                global maximumpercentage
                global quizname
                global flag1
                quizname = ''
                flag1 = 0
                maximumpercentage = 0

                for d in data:
                    if maximumpercentage < d.percentage:
                        maximumpercentage = d.percentage
                        quizname = d.quiz_id.quiz_title
                edata = enrolldata.objects.get(course_id=course.objects.get(pk=quiz_data.content_id.course_id.id),
                                               student_id=student.objects.get(pk=request.session.get('userid')))
                pdata = edata.progress_data.split(",")

                for pd in pdata:
                    if pd == quizname:
                        flag1 = 1
                if flag1 == 0:
                    if maximumpercentage > 60:
                        enrolldata.objects.filter(course_id=course.objects.get(pk=quiz_data.content_id.course_id.id),
                                                  student_id=student.objects.get(pk=request.session.get('userid'))).update(
                            progress_data=edata.progress_data + quizname + ",", course_progress=float(edata.course_progress) + float(quiz_data.quiz_weightage))

            # return HttpResponse({'username': username, 'course': courseobj, 'content': contentobj, 'quiz_data': quiz_data,
            #                   'reviewuser': review_user, 'sub_data': submission_data})

            final = enrolldata.objects.get(course_id=courseid, student_id=student.objects.get(pk=request.session.get('userid')))
            if final.course_progress == '100.0':
                a = ''
                for i in range(5):
                    if random.choice('01') == '0':
                        a += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
                    else:
                        a += random.choice('0123456789')
                b = ''
                for i in range(5):
                    if random.choice('01') == '0':
                        b += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
                    else:
                        b += random.choice('0123456789')
                c1 = ''
                for i in range(5):
                    if random.choice('01') == '0':
                        c1 += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
                    else:
                        c1 += random.choice('0123456789')


                try:
                    find1=certificate.objects.get(course_id=course.objects.get(pk=final.course_id.id),student_id=student.objects.get(pk=request.session.get('userid')))
                    pos=find1.certificate_url.rfind('/')
                    print('try')
                    sub_data=submissions.objects.filter(quiz_id__content_id__course_id=quiz_data.content_id.course_id,student_id=student.objects.get(pk=request.session.get('userid')))
                    final_score=[]
                    qlist=[]
                    for sdata in sub_data:
                        qlist.append(sdata.quiz_id.id)
                    quiz_list=set(qlist)
                    #print(quiz_list)
                    for ql in quiz_list:

                        qsub=submissions.objects.filter(quiz_id__content_id__course_id=quiz_data.content_id.course_id,student_id=student.objects.get(pk=request.session.get('userid')),quiz_id=quiz.objects.get(pk=int(ql)))
                        maximum=60.0
                        finalr=0.0
                        for qs in qsub:
                            if qs.percentage > maximum:
                                maximum = qs.percentage
                                finalr=maximum * float(qs.quiz_id.quiz_weightage) / 100
                        final_score.append(finalr)

                    #print(sum(final_score))
                    find1.scores_achieved = sum(final_score)
                    find1.save()
                    return render(request, 'course/submit.html',
                                  {'username': username, 'course': courseobj, 'content': contentobj, 'quiz_data': quiz_data,
                                   'reviewuser': review_user, 'sub_data': submission_data, 'message': 'y',
                                   'certi_url': find1.certificate_url[pos+1:len(find1.certificate_url)-4]})
                except:
                    #print('except')
                    sub_data = submissions.objects.filter(quiz_id__content_id__course_id=quiz_data.content_id.course_id,
                                                          student_id=student.objects.get(pk=request.session.get('userid')))
                    final_score = []
                    qlist = []
                    for sdata in sub_data:
                        qlist.append(sdata.quiz_id.id)
                    quiz_list = set(qlist)
                    # print(quiz_list)
                    for ql in quiz_list:

                        qsub = submissions.objects.filter(quiz_id__content_id__course_id=quiz_data.content_id.course_id,
                                                          student_id=student.objects.get(pk=request.session.get('userid')),
                                                          quiz_id=quiz.objects.get(pk=int(ql)))
                        maximum = 60.0
                        finalr = 0.0
                        for qs in qsub:
                            if qs.percentage > maximum:
                                maximum = qs.percentage
                                finalr = maximum * float(qs.quiz_id.quiz_weightage) / 100
                        final_score.append(finalr)
                    c = canvas.Canvas(
                        MEDIA_ROOT + '/Certificates/' + a + str(final.student_id.id) + b + str(
                            final.course_id.id) + c1 + '.pdf',
                        pagesize=landscape(letter))
                    c.setFont('Helvetica', 48, leading=None)
                    c.drawCentredString(415, 500, "Certification of Completion")
                    c.setFont('Helvetica', 24, leading=None)
                    c.drawCentredString(415, 450, "This Certificate is presented to :")
                    c.setFont('Helvetica-Bold', 34, leading=None)
                    c.drawCentredString(415, 395, final.student_id.fname + final.student_id.lname)
                    c.setFont('Helvetica', 24, leading=None)
                    c.drawCentredString(415, 350, "for completing the following course :")
                    c.setFont('Helvetica', 20, leading=None)
                    c.drawCentredString(415, 310, final.course_id.cname)
                    seal = MEDIA_ROOT + '/' + 'seal_stamp.png'
                    c.drawImage(seal, 330, 50, width=None, height=None)
                    c.setFont('Helvetica', 12, leading=None)
                    c.drawCentredString(415, 10, "verify at :- 127.0.0.1:8000/course/certificate/" + str(
                        final.student_id.id) + "/" + a + str(final.student_id.id) + b + str(final.course_id.id) + c1 + "/")
                    c.showPage()
                    c.save()

                    add_certi = certificate(course_id=course.objects.get(pk=final.course_id.id),
                                            student_id=student.objects.get(pk=request.session.get('userid')),
                                            certificate_url=str(
                                                MEDIA_ROOT + '/Certificates/' + a + str(final.student_id.id) + b + str(
                                                    final.course_id.id) + c1 + '.pdf'),
                                            issue_date=str(datetime.datetime.now().strftime('%d/%m/%Y')),scores_achieved=sum(final_score))
                    add_certi.save()

                    return render(request, 'course/submit.html',
                              {'username': username, 'course': courseobj, 'content': contentobj, 'quiz_data': quiz_data,
                               'reviewuser': review_user, 'sub_data': submission_data, 'message': 'y',
                               'certi_url': a + str(final.student_id.id) + b + str(final.course_id.id) + c1})

            else:
                return render(request, 'course/submit.html',
                              {'username': username, 'course': courseobj, 'content': contentobj, 'quiz_data': quiz_data,
                               'reviewuser': review_user, 'sub_data': submission_data, 'message': 'n'})
        except:
            quiz_data = quiz.objects.get(pk=quiz_id)
            courseid = course.objects.get(pk=quiz_data.content_id.course_id.id)
            course_id=courseid.id
            faqlist = faq.objects.filter(course_id=course_id)
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by(
                'content_sequence_no')
            contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0).order_by(
                'content_sequence_no')
            courseobj = course.objects.get(id=courseid.id)
            try:
                review_course = review.objects.filter(course_id=course.objects.get(pk=course_id), flag='y')
            except:
                review_course = None
            try:
                forumobj = Forum.objects.get(courseid=courseid)
                forumlink = forumobj.pk

                if 'userid' in request.session:
                    obj = student.objects.get(pk=request.session['userid'])
                    username = obj.uname
                    nav = 'logout'
                else:
                    username = 'Guest,Plz Login'
                    nav = 'register'
                try:
                    user_data = student.objects.get(pk=request.session['userid'])
                    entry = enrolldata.objects.get(student_id=user_data, course_id=courseid)
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'message': 'Already Registered',
                        'username': username,
                        'forumid': forumlink,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
                except:
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'username': username,
                        'forumid': forumlink,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
            except:

                if 'userid' in request.session:
                    obj = student.objects.get(pk=request.session['userid'])
                    username = obj.uname
                    nav = 'logout'
                else:
                    username = 'Guest,Plz Login'
                    nav = 'register'
                try:
                    user_data = student.objects.get(pk=request.session['userid'])
                    entry = enrolldata.objects.get(student_id=user_data, course_id=course_id)
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'message': 'Already Registered',
                        'username': username,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
                except:
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'username': username,

                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)

    else:
        return HttpResponseRedirect('/joinus/login/')

def syllabus(request, course_id):
    if request.session.get('userid') != None:
        try:
            find = enrolldata.objects.get(course_id=course.objects.get(pk=course_id),
                                          student_id=student.objects.get(pk=request.session.get('userid')))
            courseid = course.objects.get(pk=course_id)
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by('content_sequence_no')
            contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0).order_by('content_sequence_no')
            courseobj = course.objects.get(id=courseid.id)
            obj = student.objects.get(pk=request.session['userid'])
            username = obj.uname
            global review_user
            review_user = None
            try:
                review_course = review.objects.filter(course_id=course.objects.get(pk=course_id), flag='y')
            except:
                None
            try:
                review_user = review.objects.get(course_id=course.objects.get(pk=course_id),
                                                 student_id=student.objects.get(pk=request.session.get('userid')))
            except:
                None
            try:
                forumobj = Forum.objects.get(courseid=courseid)
                forumlink = forumobj.pk
            except:
                forumlink = -1

            d = {}
            try:
                a = []
                cdata = coursecontent.objects.filter(course_id=course_id)
                for c in cdata:
                    try:
                        quiz_data = quiz.objects.filter(content_id=c.pk).exclude(hide=1)
                        for q in quiz_data:
                            a.append(q.quiz_title)
                            a.append(c.content_name)
                        d = dict(itertools.zip_longest(*[iter(a)] * 2, fillvalue=""))

                    except:
                        None
            except:
                d = {}
            try:
                resources_data=resources1.objects.filter(content_id__course_id=course.objects.get(pk=course_id)).order_by('sequence_no')
            except:
                resources_data=''
            try:
                progress_obj = course_progress.objects.get(course_id=course.objects.get(pk=course_id),
                                                           student_id=student.objects.get(pk=request.session.get('userid')))
            except:
                progress_obj = None
            args = {
                'reviewuser': review_user,
                'reviews': review_course,
                'username': username,
                'progress': progress_obj,
                'course': courseobj,
                'content': contentobj,
                'subcontent': contentobj1,
                'course_quizes': d,
                'quizes': quiz.objects.all().exclude(hide=1),
                'forumid': forumlink,
                'resources_data':resources_data
            }
            return render(request, 'course/syllabus.html', args)
        except:

            courseid = course.objects.get(pk=course_id)
            faqlist = faq.objects.filter(course_id=course_id)
            contentobj = coursecontent.objects.filter(course_id=courseid.id, content_sub_id=0).order_by(
                'content_sequence_no')
            contentobj1 = coursecontent.objects.filter(course_id=courseid.id).exclude(content_sub_id=0).order_by(
                'content_sequence_no')
            courseobj = course.objects.get(id=courseid.id)
            try:
                review_course = review.objects.filter(course_id=course.objects.get(pk=course_id), flag='y')
            except:
                review_course = None
            try:
                forumobj = Forum.objects.get(courseid=courseid)
                forumlink = forumobj.pk

                if 'userid' in request.session:
                    obj = student.objects.get(pk=request.session['userid'])
                    username = obj.uname
                    nav = 'logout'
                else:
                    username = 'Guest,Plz Login'
                    nav = 'register'
                try:
                    user_data = student.objects.get(pk=request.session['userid'])
                    entry = enrolldata.objects.get(student_id=user_data, course_id=course_id)
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'message': 'Already Registered',
                        'username': username,
                        'forumid': forumlink,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
                except:
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'username': username,
                        'forumid': forumlink,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
            except:

                if 'userid' in request.session:
                    obj = student.objects.get(pk=request.session['userid'])
                    username = obj.uname
                    nav = 'logout'
                else:
                    username = 'Guest,Plz Login'
                    nav = 'register'
                try:
                    user_data = student.objects.get(pk=request.session['userid'])
                    entry = enrolldata.objects.get(student_id=user_data, course_id=course_id)
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'message': 'Already Registered',
                        'username': username,
                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
                except:
                    args = {
                        'course': courseobj,
                        'content': contentobj,
                        'subcontent': contentobj1,
                        'nav': nav,
                        'faqlist': faqlist,
                        'reviews': review_course,
                        'username': username,

                        'data': len(enrolldata.objects.filter(course_id=course.objects.get(pk=course_id)))
                    }
                    return render(request, 'course/view_course.html', args)
    else:
        return HttpResponseRedirect('/joinus/login/')

def certificate1(request,student_id,certificate_url):
    data=certificate.objects.filter(student_id=student.objects.get(pk=student_id))
    global cid
    cid=0
    for d in data:
        if d.certificate_url.find(certificate_url) != -1:
            cid=d.id
            break
        else:
            None

    return render(request, 'course/course_completion.html', {'certificate': certificate.objects.get(pk=cid),'url':certificate_url})