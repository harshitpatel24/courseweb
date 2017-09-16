import datetime

from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render

from blog.forms import post_descriptionForm
from blog.models import blog_post
# Create your views here.
from joinus.models import student


def create(request):
    global flag
    if 'userid' in request.session:
        form = post_descriptionForm
        if request.method == 'POST':
            form = post_descriptionForm(request.POST)
            title = request.POST.get('title')
            data = request.POST.get('post_description')
            try:
                existing = blog_post.objects.get(post_sub_id=0,
                                                 student_id=student.objects.get(pk=request.session.get('userid')))
                blog_name = existing.blog_name
                if data == '':
                    return render(request, 'blog/form.html',
                                  {'form': form, 'flag': flag, 'blog_name': blog_name, 'errormessage': 'Post Description cant be Empty',
                                   'username': student.objects.get(pk=request.session.get('userid')),'title':title})
                else:

                    post_object = blog_post(student_id=student.objects.get(pk=request.session.get('userid')),
                                        post_sub_id=existing.pk,
                                        blog_name=existing.blog_name, post_title=title, post_description=data,
                                        date=str(datetime.datetime.now().strftime('%d/%m/%Y')),
                                        time=str(datetime.datetime.now().strftime('%H:%M')), count=1)
                    post_object.save()
                    blog_post.objects.filter(post_sub_id=0,
                                         student_id=student.objects.get(pk=request.session.get('userid'))).update(
                        date=str(datetime.datetime.now().strftime('%d/%m/%Y')),
                        time=str(datetime.datetime.now().strftime('%H:%M')), count=str(int(existing.count) + 1))

                    flag = True
                    return render(request, 'blog/form.html',
                              {'form': form, 'flag': flag, 'blog_name': blog_name, 'message': 'success',
                               'username': student.objects.get(pk=request.session.get('userid'))})
            except:
                b_name = request.POST.get('blog_name')
                if data == '':
                    return render(request, 'blog/form.html',
                                  {'form': form, 'flag': flag, 'blog_name': b_name, 'errormessage': 'Post Description cant be Empty',
                                   'username': student.objects.get(pk=request.session.get('userid')),'title':title})
                else:
                    post_object = blog_post(student_id=student.objects.get(pk=request.session.get('userid')), post_sub_id=0,
                                            blog_name=b_name, post_title=title, post_description=data,
                                            date=str(datetime.datetime.now().strftime('%d/%m/%Y')),
                                            time=str(datetime.datetime.now().strftime('%H:%M')), count=1)
                    post_object.save()
                    return render(request, 'blog/form.html', {'form': form, 'message': 'success',
                                                              'username': student.objects.get(
                                                                  pk=request.session.get('userid'))})
        else:

            flag = False
            try:
                existing = blog_post.objects.get(post_sub_id=0,
                                                 student_id=student.objects.get(pk=request.session.get('userid')))
                blog_name = existing.blog_name
                flag = True
                return render(request, 'blog/form.html', {'form': form, 'flag': flag, 'blog_name': blog_name,
                                                          'username': student.objects.get(
                                                              pk=request.session.get('userid'))})
            except:
                flag = False
                return render(request, 'blog/form.html', {'form': form, 'flag': flag, 'username': student.objects.get(
                    pk=request.session.get('userid')),'blog_name':''})
    else:
        return HttpResponseRedirect('/joinus/login/')


def view_blog(request):
    if 'userid' in request.session:
        try:
            blog_data = blog_post.objects.filter(post_sub_id=0).exclude(
                student_id=student.objects.get(pk=request.session.get('userid')))
        except:
            blog_data = ''
        try:
            user_blog_data = blog_post.objects.get(post_sub_id=0,
                                                   student_id=student.objects.get(pk=request.session.get('userid')))
        except:
            user_blog_data = None
        return render(request, 'blog/blog.html', {'blog_data': blog_data, 'user_blog_data': user_blog_data,
                                                  'username': student.objects.get(pk=request.session.get('userid')),
                                                  'nav': 'logout'})
    else:
        try:
            blog_data = blog_post.objects.filter(post_sub_id=0)
        except:
            blog_data = ''
        return render(request, 'blog/blog.html', {'blog_data': blog_data, 'user_blog_data': None,
                                                  'username': 'Guest,Plz Login', 'nav': 'register'})


def visit_blog(request, blog_id):
    blog_data = blog_post.objects.filter(Q(pk=blog_id) | Q(post_sub_id=blog_id)).order_by('-pk')
    try:
        return render(request, 'blog/visit_blog.html',
                      {'blog_data': blog_data, 'username': student.objects.get(pk=request.session.get('userid')),
                       'nav': 'logout'})
    except:
        return render(request, 'blog/visit_blog.html',
                      {'blog_data': blog_data, 'username': 'Guest,Plz Login', 'nav': 'register'})
