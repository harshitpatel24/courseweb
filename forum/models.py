from django.contrib.auth.models import User
from django.db import models
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from django import forms

from instructor.models import course
from joinus.models import instructor,student
# Create your models here.
class Forum(models.Model):
    title = models.CharField(max_length=60)
    description = models.TextField(blank=True, default='')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now=True)
    courseid=models.ForeignKey(course,blank=True,null=True)
    creator = models.ForeignKey(instructor, blank=True, null=True)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    def num_posts(self):
        return sum([t.num_posts() for t in self.topic_set.all()])

    def last_post(self):
        if self.topic_set.count():
            last = None
            for t in self.topic_set.all():
                l = t.last_post()
                if l:
                    if not last:
                        last = l
                    elif l.created > last.created:
                        last = l
            return last

class Topic(models.Model):
    title = models.CharField(max_length=60)
    description = models.TextField(max_length=10000, blank=True, null=True)
    forum = models.ForeignKey(Forum)
    created = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(student, blank=True, null=True)
    by_instructor=models.ForeignKey(instructor,blank=True,null=True)
    updated = models.DateTimeField(auto_now=True)
    closed = models.BooleanField(blank=True, default=False)

    def num_posts(self):
        return self.post_set.count()
    def __str__(self):
        return  self.title

    def num_replies(self):
        return max(0, self.post_set.count())

    def last_post(self):
        if self.post_set.count():
            return self.post_set.latest('created')
    def last_post_instructor(self):
        if self.post_set.count():
            return self.post_set.latest('by_instructor')
    def __unicode__(self):
        return unicode(self.creator) + " - " + self.title

class Post(models.Model):
    title = models.CharField(max_length=60)
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(student, blank=True, null=True)
    by_instructor = models.ForeignKey(instructor, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey(Topic)
    body = models.TextField(max_length=10000)
    user_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.title
    def __unicode__(self):
        return u"%s - %s - %s" % (self.creator, self.topic, self.title)

    def short(self):
        return u"by- %s  in %s\n on %s" % (self.creator, self.title, self.created.strftime("%b %d, %I:%M %p"))

    def short_name(self):
        return u" %s "%(self.creator)

    def short_instructorname(self):
        return u" %s "%(self.by_instructor)

    def short_title(self):
        return u" %s "% (self.topic.last_post())

    def short_date(self):
        return u" %s " % (self.created.strftime("%b %d, %I:%M %p"))

    short.allow_tags = True
    short_name.allow_tags = True
    short_title.allow_tags = True
    short_date.allow_tags = True

class ProfaneWord(models.Model):
    word = models.CharField(max_length=60)

    def __str__(self):
        return self.word
    def __unicode__(self):
        return self.word


