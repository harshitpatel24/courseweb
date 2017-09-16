import random
import string

from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from joinus import models
import joinus
from joinus.models import student, otp_generator
from django.core.files.storage import FileSystemStorage



def register(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname=request.POST.get('lname')
        uname=request.POST.get('uname')
        email=request.POST.get('email')
        password=request.POST.get('pass')
        myfile = request.FILES['file1']
        try:
            data=student.objects.get(email=email)
            message="Email Already Registered !!"
            return render(request,'joinus/register.html',{'message':message})
        except:
            student_object=student(fname=fname,lname=lname,uname=uname,email=email,password=password,pic=myfile,flag='0')
            student_object.save()
            a=''
            for i in range(5):

                if random.choice('01') == '0':
                    a+=random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
                else:
                    a+=random.choice('0123456789')
            otp_data=otp_generator(student_id=student.objects.get(pk=student_object.id),otp=a)
            otp_data.save()
            send_mail(
                'OTP for CourseWeb Authentication',
                'Your OTP is : '+ a,
                'harshitus99@gmail.com',
                [student_object.email],
                fail_silently=False,
            )
            message="Successfully Registered !!"

        if 'userid' in request.session:
            obj=student.objects.get(pk=request.session['userid'])
            username=obj.uname
        else:
            username='Guest'
        return render(request,'joinus/otpcheck.html',{'username':username,'id':student_object.id})
    else:
        return render(request,'joinus/register.html',{'username':'Guest,Plz Login'})

def login(request):

    if 'userid' in request.session:
        obj = student.objects.get(pk=request.session['userid'])
        username=obj.uname
        args = {  # 'instructor': globals()['loggedin'],
            'user1': obj,
            'username': username,
        }
        return HttpResponseRedirect('/home/',args)
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('pass')
            student_list = student.objects.all()

            for student_data in student_list:

                if password == student_data.password and email == student_data.email:
                    if student_data.flag == '0':
                        if 'userid' in request.session:
                            obj = student.objects.get(pk=request.session['userid'])
                            username = obj.uname
                        else:
                            username = 'Guest'

                        return render(request, 'joinus/otpcheck.html', {'username': username, 'id': student_data.id})
                    #  globals()['loggedin']=instructor_data
                    request.session['userid'] = student_data.pk
                    obj = student.objects.get(pk=request.session['userid'])
                    username=obj.uname
                    args = {'user1': obj,
                            'username':username}
                    return HttpResponseRedirect('/home/', args)
            return render(request, 'joinus/login.html',{'message':'Wrong Username or Password','username':'Guest'})
        else:
            return render(request, 'joinus/login.html',{'username':'Guest,Plz Login'})

def checklogin(request):
    if request.user != None:
        user = request.user
        uname = request.user.username
        email=user.email
        password=user.password
        fname=request.user.get_short_name()
        lname=request.user.last_name

        try:
            check_obj=student.objects.get(email=email)

        except:
            student_object = student(fname=fname, lname=lname, uname=uname, email=email, password=password)
            student_object.save()
        finally:
            student_list = student.objects.all()
            for student_data in student_list:
                if  email == student_data.email:
                    #  globals()['loggedin']=instructor_data
                    request.session['userid'] = student_data.pk
                    obj = student.objects.get(pk=request.session['userid'])
                    username=obj.uname
                    args = {  # 'instructor': globals()['loggedin'],
                    'user1': obj,
                    'username': username,
                    }
                    return HttpResponseRedirect('/home/', args)
    else:
        return HttpResponseRedirect('/joinus/login/')

def demo(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pass')

        users = student.objects.all()
        for user in users:
            if password == user.password and email == user.email:
                args = {'user1': user}
        return render(request, 'home/home.html', args)
        #if not user.exists():
        #    return render(request, 'joinus/login.html')

def signout(request):
    if 'userid' in request.session:
        del request.session['userid']
    return HttpResponseRedirect('/home/')

def verify(request,user_id):
    obj = student.objects.get(pk=user_id)
    username = obj.uname
    otp=request.POST.get('otp')

    if otp == otp_generator.objects.get(student_id=student.objects.get(pk=user_id)).otp:
        student.objects.filter(id=user_id).update(flag='1')

        otp_generator.objects.filter(student_id=student.objects.get(pk=user_id)).delete()

        request.session['userid'] = user_id
        args = {  # 'instructor': globals()['loggedin'],
            'user1': obj,
            'username': username,
        }
        return HttpResponseRedirect('/home/', args)
    else:
        return render(request,'joinus/otpcheck.html',{'message':'You Entered Wrong OTP !','username':username,'id':user_id})


def sendagain(request,user_id):
    obj = student.objects.get(pk=user_id)
    username = obj.uname
    a = ''
    for i in range(5):

        if random.choice('01') == '0':
            a += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        else:
            a += random.choice('0123456789')
    student_object=student.objects.get(pk=user_id)
    otp_generator.objects.filter(student_id=student.objects.get(pk=student_object.id)).update(otp=a)
    send_mail(
        'OTP for CourseWeb Authentication',
        'Your OTP is : ' + a,
        'harshitus99@gmail.com',
        [student_object.email],
        fail_silently=False,
    )
    return render(request,'joinus/otpcheck.html',{'message':'New OTP has been sent !!','username':username,'id':user_id})




def forgot(request):
    if 'userid' in request.session:
        obj = student.objects.get(pk=request.session['userid'])
        username = obj.uname
        args = {  # 'instructor': globals()['loggedin'],
            'user1': obj,
            'username': username,
        }
    else:
        args={}
    return render(request,'joinus/forgot_password.html',args)

def sendotpforgot(request):
    if request.method == 'POST':
        email=request.POST.get('email')
        try:
            student_data = student.objects.get(email=email)
            try:
                otp_generator.objects.get(student_id__email=email)
                if 'userid' in request.session:
                    obj = student.objects.get(pk=request.session['userid'])
                    username = obj.uname
                    args = {  # 'instructor': globals()['loggedin'],
                        'user1': obj,
                        'username': username,
                        'id': student_data.id
                    }
                else:
                    args = {'id': student_data.id}
                return render(request, 'joinus/validateotp.html', args)
            except:
                a = ''
                for i in range(5):
                    if random.choice('01') == '0':
                        a += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
                    else:
                        a += random.choice('0123456789')
                otp_data = otp_generator(student_id=student.objects.get(pk=student_data.id), otp=a)
                otp_data.save()
                send_mail(
                    'OTP for CourseWeb Authentication',
                    'Your OTP is : ' + a,
                    'harshitus99@gmail.com',
                    [student_data.email],
                    fail_silently=False,
                )
                if 'userid' in request.session:
                    obj = student.objects.get(pk=request.session['userid'])
                    username = obj.uname
                    args = {  # 'instructor': globals()['loggedin'],
                        'user1': obj,
                        'username': username,
                        'id': student_data.id
                    }
                else:
                    args = {'id': student_data.id}
                return render(request, 'joinus/validateotp.html', args)
        except:
            return render(request, 'joinus/forgot_password.html', {'message': 'Email is not registered!!'})

def verify_forgot(request,user_id):
    obj = student.objects.get(pk=user_id)
    username = obj.uname
    otp=request.POST.get('otp')

    if otp == otp_generator.objects.get(student_id=student.objects.get(pk=user_id)).otp:
        student.objects.filter(id=user_id).update(flag='1')
        otp_generator.objects.filter(student_id=student.objects.get(pk=user_id)).delete()
        args = {  # 'instructor': globals()['loggedin'],
            'user1': obj,
            'username': username,
        }
        return render(request,'joinus/setpassword.html',{'username':username,'id':user_id})
    else:
        return render(request,'joinus/validateotp.html',{'message':'You Entered Wrong OTP !','username':username,'id':user_id})


def sendagain_forgot(request,user_id):
    obj = student.objects.get(pk=user_id)
    username = obj.uname
    a = ''
    for i in range(5):

        if random.choice('01') == '0':
            a += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        else:
            a += random.choice('0123456789')
    student_object=student.objects.get(pk=user_id)
    otp_generator.objects.filter(student_id=student.objects.get(pk=student_object.id)).update(otp=a)
    send_mail(
        'OTP for CourseWeb Authentication',
        'Your OTP is : ' + a,
        'harshitus99@gmail.com',
        [student_object.email],
        fail_silently=False,
    )
    return render(request,'joinus/validateotp.html',{'message':'New OTP has been sent !!','username':username,'id':user_id})

def set_password(request,user_id):
    if request.method == 'POST':
        obj = student.objects.get(pk=user_id)
        username = obj.uname
        pass1=request.POST.get('password')
        pass2=request.POST.get('repassword')
        if pass1 == pass2:
            student.objects.filter(pk=user_id).update(password=pass1)
            return HttpResponseRedirect('/joinus/login/')
        else:
            return render(request,'joinus/setpassword.html',{'message':'Password and Retype Password are not matched !!','username':username,'id':user_id})


def complete_profile(request):
    if request.method == 'POST':
        print("in if")
        fname = request.POST.get('fname')
        lname=request.POST.get('lname')
        uname=request.POST.get('uname')
        email=request.POST.get('email')
        password=request.POST.get('pass')
        myfile = request.FILES['file1']
        try:
            data=student.objects.get(email=email)
            message="Email Already Registered !!"
            return render(request,'joinus/complete_profile.html',{'message':message})
        except:
            student_object=student(fname=fname,lname=lname,uname=uname,email=email,password=password,pic=myfile,flag='0')
            student_object.save()
            request.session['userid'] = student_object.pk
            username=student_object.uname
            return render(request, 'joinus/complete_profile.html', {'username': username,'message':'Sucessfully Registered'})

    else:

        print("in else")
        try:
            email= joinus.pipeline.email
            data=student.objects.get(email=email)
            username=data.uname
            request.session['userid'] = data.pk
            args = {
                'username': username,
            }
            return HttpResponseRedirect('/home/',args)
        except:
            args={
                'fname': joinus.pipeline.fname,
                'lname': joinus.pipeline.lname,
                'uname': joinus.pipeline.uname,
                'email': joinus.pipeline.email,
            }
            print(joinus.pipeline.fname)
            return render(request,'joinus/complete_profile.html',args)