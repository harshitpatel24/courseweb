from django.db.models import Q
import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
# Create your views here.
from django.urls import reverse

from course.models import review, submissions, certificate
from instructor.models import enrolldata, course, coursecontent, quiz
from joinus.models import student, instructor
from student.forms import askquestionForm
from student.models import askquestion
import itertools

def student_panel(request):
    if request.session.get('userid') != None:
        stu_id = request.session['userid']
        data = student.objects.get(id=stu_id)
        args = {'user1': data,'username':student.objects.get(pk=request.session.get('userid'))}
        return render(request, 'student/student_panel.html', args)
    else:
        return HttpResponseRedirect('/joinus/login/')


def edit_profile(request):
    if request.session.get('userid') != None:
        if request.method == 'POST':
            if request.FILES:
                student.objects.filter(id=request.session['userid']).update(fname=request.POST.get('fname'),
                                                                            lname=request.POST.get('lname'),
                                                                            uname=request.POST.get('uname'),
                                                                            email=request.POST.get('email'),
                                                                            pic=request.FILES['file1'])
                data = student.objects.get(id=request.session['userid'])
                args = {'user1': data, 'message': 'success'}
            else:
                student.objects.filter(id=request.session['userid']).update(fname=request.POST.get('fname'),
                                                                            lname=request.POST.get('lname'),
                                                                            uname=request.POST.get('uname'),
                                                                            email=request.POST.get('email'),
                                                                            )
                data = student.objects.get(id=request.session['userid'])
                args = {'user1': data, 'message': 'success','username':student.objects.get(pk=request.session.get('userid'))}
            return render(request, 'student/edit_profile.html', args)
        else:
            data = student.objects.get(id=request.session['userid'])
            args = {'user1': data,'username':student.objects.get(pk=request.session.get('userid'))}
            return render(request, 'student/edit_profile.html', args)
    else:
        return HttpResponseRedirect('/joinus/login/')


def change_password(request):
    if request.session.get('userid') != None:
        if request.method == 'POST':
            data = student.objects.get(id=request.session['userid'])
            if request.POST.get('password') == data.password:
                if request.POST.get('newpassword') == request.POST.get('renewpassword'):
                    student.objects.filter(id=request.session['userid']).update(
                        password=request.POST.get('newpassword'))
                    args = {'user1': data, 'message1': 'Password Change Successfully !!','username':student.objects.get(pk=request.session.get('userid'))}
                    return render(request, 'student/change_password.html', args)
                else:
                    args = {'user1': data, 'message': 'New and Retype Password are not same !!','username':student.objects.get(pk=request.session.get('userid'))}
                    return render(request, 'student/change_password.html', args)
            else:
                args = {'user1': data, 'message': 'Current Password is wrong !!','username':student.objects.get(pk=request.session.get('userid'))}
                return render(request, 'student/change_password.html', args)
        else:
            data = student.objects.get(id=request.session['userid'])
            args = {'user1': data,'username':student.objects.get(pk=request.session.get('userid'))}
            return render(request, 'student/change_password.html', args)
    else:
        return HttpResponseRedirect('/joinus/login/')


def enrolled_course(request):
    try:
        enroll_data = enrolldata.objects.filter(student_id=student.objects.get(pk=request.session.get('userid'))).exclude(course_progress='100.0')
    except:
        enroll_data = ''
    try:
        completed_data=enrolldata.objects.filter(course_progress='100.0',student_id=student.objects.get(pk=request.session.get('userid')))
    except:
        completed_data=''
    return render(request, 'student/enrolled_student.html', {'courses': enroll_data,'username':student.objects.get(pk=request.session.get('userid')),'completed':completed_data})

def ask_question(request, course_id):
    if request.session.get('userid') != None:
        form = askquestionForm
        course_data = course.objects.get(pk=course_id)
        contentobj = coursecontent.objects.filter(course_id=course_data.id, content_sub_id=0)
        try:

            reviewuser = review.objects.get(course_id=course.objects.get(pk=course_id),
                                    student_id=student.objects.get(pk=request.session.get('userid')))
        except:
            reviewuser=None
        return render(request, 'student/ask_question.html', {'form': form,'course': course_data, 'content': contentobj,'username':student.objects.get(pk=request.session.get('userid')),'reviewuser':reviewuser})
    else:
        return HttpResponseRedirect('/joinus/login/')


def ask_question_display(request, course_id):

    data1 = askquestion.objects.filter(student_id=student.objects.get(pk=request.session.get('userid')),
                                       course_id=course.objects.get(pk=course_id),
                                       question_subid=0).order_by('reply_flag')
    course_data = course.objects.get(pk=course_id)
    contentobj = coursecontent.objects.filter(course_id=course_data.id, content_sub_id=0)
    if request.method == 'POST':
        form = askquestionForm(request.POST)
        qhead = request.POST.get('qheading')
        qdesc = request.POST.get('question_description')
        c_data = course.objects.get(pk=course_id)
        if qdesc == '':
            try:
                reviewuser = review.objects.get(course_id=course.objects.get(pk=course_id),
                                                student_id=student.objects.get(pk=request.session.get('userid')))
            except:
                reviewuser = None
            return render(request, 'student/ask_question.html',
                          {'form': form, 'course': course_data, 'content': contentobj,'errormessage':'Question Description Shoul not be Empty',
                           'username': student.objects.get(pk=request.session.get('userid')), 'reviewuser': reviewuser,'qhead':qhead})
        else:
            try:
                data2 = askquestion.objects.get(student_id=student.objects.get(pk=request.session.get('userid')),
                                                course_id=c_data,
                                                question_heading=qhead,
                                                question_description=qdesc)
            except:
                data = askquestion(student_id=student.objects.get(pk=request.session.get('userid')),
                                   course_id=c_data,
                                   instructor_id=instructor.objects.get(pk=c_data.creatorid.id),
                                   question_heading=qhead,
                                   question_description=qdesc, reply_description='', sequence_no=1,
                                   question_date=str(datetime.datetime.now().strftime("%d/%m/%Y")),
                                   question_time=str(datetime.datetime.now().strftime("%H:%M")),
                                   reply_date='',
                                   reply_time='',
                                   question_flag='y',
                                   reply_flag='n')
                data.save()
            data1 = askquestion.objects.filter(student_id=student.objects.get(pk=request.session.get('userid')),
                                               course_id=course.objects.get(pk=course_id), question_subid=0).order_by(
                'reply_flag')
            remaining = askquestion.objects.filter(student_id=student.objects.get(pk=request.session.get('userid')),
                                                   question_subid=0, course_id=course.objects.get(pk=course_id),
                                                   reply_flag='n').count()
            #print(remaining)
            try:
                reviewuser = review.objects.get(course_id=course.objects.get(pk=course_id),
                                            student_id=student.objects.get(pk=request.session.get('userid')))
            except:
                reviewuser=None
            return render(request, 'student/ask_question_panel.html',
                          {'questions': data1, 'remaining': remaining, 'course': course_data, 'content': contentobj,'username':student.objects.get(pk=request.session.get('userid')),'reviewuser':reviewuser})
    else:
        try:
            reviewuser = review.objects.get(course_id=course.objects.get(pk=course_id),
                                        student_id=student.objects.get(pk=request.session.get('userid')))
        except:
            reviewuser=None
        remaining = askquestion.objects.filter(student_id=student.objects.get(pk=request.session.get('userid')),
                                               question_subid=0, course_id=course.objects.get(pk=course_id),
                                               reply_flag='n').count()

        return render(request, 'student/ask_question_panel.html',
                      {'questions': data1, 'remaining': remaining, 'course': course_data, 'content': contentobj,'username':student.objects.get(pk=request.session.get('userid')),'reviewuser':reviewuser})


def view_question(request, question_id):
    question_data = askquestion.objects.filter(Q(question_subid=question_id) | Q(pk=question_id))
    data2 = askquestion.objects.get(pk=question_id)
    form = askquestionForm
    data1 = course.objects.get(pk=data2.course_id.id)
    course_data = course.objects.get(pk=data1.id)
    contentobj = coursecontent.objects.filter(course_id=course_data.id, content_sub_id=0)
    try:
        reviewuser = review.objects.get(course_id=course.objects.get(pk=data2.course_id.id),
                                    student_id=student.objects.get(pk=request.session.get('userid')))
    except:
        reviewuser=None
    return render(request, 'student/view_question.html',
                  {'question_data': question_data,'form':form, 'question_id': question_id, 'message': '', 'course': course_data,'username':student.objects.get(pk=request.session.get('userid')),
                   'content': contentobj,'reviewuser':reviewuser})


def continue_conversation(request, question_id):
    if request.method == 'POST':
        form = askquestionForm
        newque = request.POST.get('question_description')
        question_data = askquestion.objects.filter(Q(question_subid=question_id) | Q(pk=question_id))
        data2 = askquestion.objects.get(pk=question_id)
        data1 = course.objects.get(pk=data2.course_id.id)
        course_data = course.objects.get(pk=data1.id)
        contentobj = coursecontent.objects.filter(course_id=course_data.id, content_sub_id=0)
        for qdata in question_data:
            if qdata.reply_description == '':
                message = "You Have to wait for instructor's reply"
                return render(request, 'student/view_question.html',
                              {'question_data': question_data, 'question_id': question_id, 'message': message,
                               'course': course_data,
                               'content': contentobj,'username':student.objects.get(pk=request.session.get('userid'))})
            else:
                None
        try:
            data1 = askquestion.objects.get(pk=question_id)
            question_data1 = askquestion.objects.filter(question_subid=question_id).count()
            try:
                data = askquestion.objects.get(question_subid=question_id, question_description=newque)
            except:
                qid = askquestion.objects.get(pk=question_id)
                course1 = course.objects.get(pk=qid.course_id.id)
                askquestion.objects.filter(pk=question_id).update(question_flag='y')
                data = askquestion(student_id=data1.student_id, course_id=course1,
                                   instructor_id=instructor.objects.get(pk=course1.creatorid.id),
                                   question_subid=data1.pk,
                                   question_heading=data1.question_heading, question_description=newque,
                                   reply_description='',
                                   sequence_no=str(question_data1 + 1),
                                   question_date=str(datetime.datetime.now().strftime("%d/%m/%Y")),
                                   question_time=str(datetime.datetime.now().strftime("%H:%M")),
                                   reply_date='',
                                   reply_time='',
                                   )
                data.save()
                askquestion.objects.filter(pk=data1.pk).update(reply_flag='n')
        except:
            data1 = askquestion.objects.get(pk=question_id)
            askquestion.objects.filter(pk=question_id).update(question_flag='y')
            question_data1 = askquestion.objects.filter(question_subid=question_id).count()
            data = askquestion(student_id=data1.student_id, course_id=course1,
                               instructor_id=instructor.objects.get(pk=course1.creatorid.id),
                               question_subid=data1.pk,
                               question_heading=data1.question_heading, question_description=newque,
                               reply_description='',
                               sequence_no=str(question_data1 + 1),
                               question_date=str(datetime.datetime.now().strftime("%d/%m/%Y")),
                               question_time=str(datetime.datetime.now().strftime("%H:%M")),
                               reply_date='',
                               reply_time='', )
            data.save()
            askquestion.objects.filter(pk=data1.pk).update(reply_flag='n')
        data2 = askquestion.objects.get(pk=question_id)
        data1 = course.objects.get(pk=data2.course_id.id)
        contentobj = coursecontent.objects.filter(course_id=data1, content_sub_id=0)
        question_data = askquestion.objects.filter(Q(question_subid=question_id) | Q(pk=question_id))
        return render(request, 'student/view_question.html',
                      {'question_data': question_data, 'question_id': question_id, 'message': '', 'course': course_data,
                       'content': contentobj,'username':student.objects.get(pk=request.session.get('userid'))})
    else:
        question_data = askquestion.objects.filter(Q(question_subid=question_id) | Q(pk=question_id))
        data2 = askquestion.objects.get(pk=question_id)
        data1 = course.objects.get(pk=data2.course_id.id)
        contentobj = coursecontent.objects.filter(course_id=data1, content_sub_id=0)
        return render(request, 'student/view_question.html',
                      {'question_data': question_data, 'question_id': question_id, 'message': '', 'course': data1,
                       'content': contentobj,'username':student.objects.get(pk=request.session.get('userid'))})

def all_questions(request):
    remaining = askquestion.objects.filter(question_subid=0,
                                           student_id=student.objects.get(pk=request.session.get('userid')),
                                           reply_flag='n').order_by('course_id__cname')
    courses = askquestion.objects.filter(question_subid=0,
                                         student_id=student.objects.get(
                                             pk=request.session.get('userid'))).values(
                                            'course_id__cname').distinct()
    b = []
    for remain in remaining:
        b.append(remain.course_id.cname)
    a = []
    for course in courses:
        for k, v in course.items():
            a.append(v)
            a.append(b.count(v))
    a.append('general')
    a.append(len(remaining))
    d = dict(itertools.zip_longest(*[iter(a)] * 2, fillvalue=""))
    questions = askquestion.objects.filter(student_id=student.objects.get(pk=request.session.get('userid')),
                                           question_subid=0).order_by('reply_flag')
    return render(request,'student/all_questions.html',{'questions':questions,'courses':courses,'remaining': d,'username':student.objects.get(pk=request.session.get('userid'))})

def myprogress(request):
    courses=enrolldata.objects.filter(student_id=student.objects.get(pk=request.session.get('userid')))
    data=submissions.objects.filter(student_id=student.objects.get(pk=request.session.get('userid'))).order_by('-pk')
    return render(request,'student/myprogress.html',{'username':student.objects.get(pk=request.session.get('userid')),'data':data,'courses':courses})

def accomplishments(request):
    try:
        data = certificate.objects.filter(student_id=student.objects.get(pk=request.session.get('userid')))
        a=[]
        for d1 in data:
            pos = d1.certificate_url.rfind('/')
            a.append(d1.id)
            a.append(d1.certificate_url[pos + 1:len(d1.certificate_url) - 4])
        #   cid = enrolldata.objects.get(student_id=student.objects.get(pk=request.session.get('userid')),
        #                                 course_id=course.objects.get(pk=d1.course_id.id))
        #    quiz_data = cid.progress_data.split(',')
        #    sub_total = []
        #    for quiz1 in quiz_data:
        #       getquiz = quiz.objects.get(quiz_title=quiz1, content_id__course_id=cid.course_id)
         #       total = 0.0
         #       data12 = submissions.objects.filter(quiz_id__content_id__course_id__id=cid.course_id.id,
         #                                           student_id=student.objects.get(pk=request.session.get('userid')),
          #                                          quiz_id__quiz_title=quiz1)
          #      for sub in data12:
          #          if sub.percentage > total:
          #              total = sub.percentage * float(getquiz.quiz_weightage) / 100
          #      sub_total.append(total)
          #  print(sub_total)

        d = dict(itertools.zip_longest(*[iter(a)] * 2, fillvalue=""))
        return render(request, 'student/accomplishments.html',
                      {'data': data, 'username': student.objects.get(pk=request.session.get('userid')),'urls':d})
    except:
        d=None
        data=None
        return render(request, 'student/accomplishments.html',
                      {'data': data, 'username': student.objects.get(pk=request.session.get('userid')), 'urls': d})
