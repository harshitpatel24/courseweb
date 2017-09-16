from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from joinus.models import instructor,student
# Create your views here.
from django.template import RequestContext

from django.forms import models as forms_models

from django.http import HttpResponseRedirect

from django.shortcuts import render_to_response, get_object_or_404

from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template.context_processors import csrf

from coursewebsite.settings import DJANGO_SIMPLE_FORUM_TOPICS_PER_PAGE, DJANGO_SIMPLE_FORUM_REPLIES_PER_PAGE
from forum.models import Forum, Topic, Post
from forum.forms import TopicForm, PostForm

#from guest.decorators import guest_allowed, login_required

from django.template import RequestContext

def index(request):
    """Main listing."""
    forums = Forum.objects.all()
    topic =Topic.objects.all()
    if 'userid' in request.session:
        status='student'
        stud_obj=student.objects.get(pk=request.session['userid'])
        username=stud_obj.uname
    elif 'instructorid' in request.session:
        status='instructor'
        inst_obj=instructor.objects.get(pk=request.session['instructorid'])
        username=inst_obj.uname
    else:
        status='guest'
        username='Guest,Plz Login'
    return render(request,'forum/list.html', {'forums': forums,
                                              'topic':topic,
                                              'username':username,
                                              'status':status})


def add_csrf(request, **kwargs):
    d = dict(user=request.user, **kwargs)
    d.update(csrf(request))
    return d


def mk_paginator(request, items, num_items):
    """Create and return a paginator."""
    paginator = Paginator(items, num_items)
    try:
        page = int(request.GET.get("page", '1'))
    except ValueError:
        page = 1

    try:
        items = paginator.page(page)
    except (InvalidPage, EmptyPage):
        items = paginator.page(paginator.num_pages)
    return items


def forum(request, forum_id):
    """Listing of topics in a forum."""
    topics = Topic.objects.filter(forum=forum_id).order_by("-created")
    topics = mk_paginator(request, topics, DJANGO_SIMPLE_FORUM_TOPICS_PER_PAGE)
    forum = get_object_or_404(Forum, pk=forum_id)

    if 'userid' in request.session:
        status='student'
        stud_obj=student.objects.get(pk=request.session['userid'])
        username=stud_obj.uname
    elif 'instructorid' in request.session:
        status='instructor'
        inst_obj=instructor.objects.get(pk=request.session['instructorid'])
        username=inst_obj.uname
    else:
        status='guest'
        username='Guest,Plz Login'

    return render(request,"forum/forum.html",add_csrf(request, topics=topics, pk=forum_id, forum=forum,username=username,status=status))


def topic(request, topic_id):
    """Listing of posts in a topic."""
    posts = Post.objects.filter(topic=topic_id).order_by("created")
    posts = mk_paginator(request, posts, DJANGO_SIMPLE_FORUM_REPLIES_PER_PAGE)
    topic = Topic.objects.get(pk=topic_id)

    if 'userid' in request.session:
        status='student'
        stud_obj=student.objects.get(pk=request.session['userid'])
        username=stud_obj.uname
    elif 'instructorid' in request.session:
        status='instructor'
        inst_obj=instructor.objects.get(pk=request.session['instructorid'])
        username=inst_obj.uname
    else:
        status='guest'
        username='Guest,Plz Login'

    return render(request,"forum/topic.html", add_csrf(request, posts=posts, pk=topic_id,
                                                                         topic=topic,username=username,status=status))

def post_reply(request, topic_id):
    if 'userid' in request.session:
        topic = Topic.objects.get(pk=topic_id)
        form=PostForm
        status = 'student'
        stud_obj = student.objects.get(pk=request.session['userid'])
        username = stud_obj.uname

        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                post = Post()
                post.topic = topic
                post.title = request.POST.get('title')
                post.body = request.POST.get('body')
                obj = student.objects.get(pk=request.session['userid'])
                post.creator = obj
                post.user_ip = request.META['REMOTE_ADDR']

                post.save()

                return HttpResponseRedirect(reverse('topic-detail', args=(topic.id,)))

        return render(request,'forum/reply.html', {
            'form': form,
            'topic': topic,
            'username': username,
            'status': status
        }, )
    elif 'instructorid' in request.session:
        topic = Topic.objects.get(pk=topic_id)
        form = PostForm
        status = 'instructor'
        inst_obj = instructor.objects.get(pk=request.session['instructorid'])
        username = inst_obj.uname

        if request.method == 'POST':
            form = PostForm(request.POST)

            if form.is_valid():
                post = Post()
                post.topic = topic
                post.title = request.POST.get('title')
                post.body = request.POST.get('body')
                obj = instructor.objects.get(pk=request.session['instructorid'])
                post.by_instructor = obj
                post.user_ip = request.META['REMOTE_ADDR']

                post.save()

                return HttpResponseRedirect(reverse('topic-detail', args=(topic.id,)))

        return render(request,'forum/reply.html', {
            'form': form,
            'topic': topic,
            'username': username,
            'status': status
        }, )
    else:
        return HttpResponseRedirect('/joinus/login/')

def new_topic(request, forum_id):
    if 'userid' in request.session:
        form = TopicForm()
        forum = get_object_or_404(Forum, pk=forum_id)

        status = 'student'
        stud_obj = student.objects.get(pk=request.session['userid'])
        username = stud_obj.uname

        if request.method == 'POST':
            form = TopicForm(request.POST)

            if form.is_valid():
                topic = Topic()
                topic.title = form.cleaned_data['title']
                topic.description = form.cleaned_data['description']
                topic.forum = forum
                obj=student.objects.get(pk=request.session['userid'])
                topic.creator = obj

                topic.save()

                return HttpResponseRedirect(reverse('forum-detail', args=(forum_id,)))

        return render(request,'forum/new-topic.html', {
            'form': form,
            'forum': forum,
            'username': username,
            'status': status
        }, )
    elif 'instructorid' in request.session:
        form = TopicForm()
        forum = get_object_or_404(Forum, pk=forum_id)

        status = 'instructor'
        inst_obj = instructor.objects.get(pk=request.session['instructorid'])
        username = inst_obj.uname

        if request.method == 'POST':
            form = TopicForm(request.POST)

            if form.is_valid():
                topic = Topic()
                topic.title = form.cleaned_data['title']
                topic.description = form.cleaned_data['description']
                topic.forum = forum
                obj=instructor.objects.get(pk=request.session['instructorid'])
                topic.by_instructor = obj

                topic.save()

                return HttpResponseRedirect(reverse('forum-detail', args=(forum_id,)))

        return render(request,'forum/new-topic.html', {
            'form': form,
            'forum': forum,
            'username': username,
            'status': status
        }, )
    else:
        return HttpResponseRedirect('/joinus/login/')

def create_forum(request):
    if 'instructorid' in request.session:

        status = 'instructor'
        inst_obj = instructor.objects.get(pk=request.session['instructorid'])
        username = inst_obj.uname

        if request.method=='POST':
            instructor_obj=instructor.objects.get(pk=request.session['instructorid'])
            title=request.POST.get('title')
            desc=request.POST.get('description')
            forum_obj=Forum(title=title,description=desc,creator=instructor_obj)
            forum_obj.save()
            return HttpResponseRedirect('/forum/',{'username':username,
                                              'status':status})
        else:
            return render(request,'forum/new-forum.html',{'username':username,
                                              'status':status})
    else:
        return HttpResponseRedirect('/instructor/login/')