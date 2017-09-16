import datetime
from django.db import models
from joinus.models import student, instructor


# Create your models here.
class categories(models.Model):
    name = models.CharField(max_length = 50)
    def __str__(self):
        return self.name

class course(models.Model):
    cname=models.CharField(max_length=50)
    cdesc=models.CharField(max_length=500,default='none')
    creatorid=models.ForeignKey(instructor,on_delete=models.CASCADE)
    category_id=models.ForeignKey(categories,on_delete=models.CASCADE)
    taughtby=models.CharField(max_length=50)
    prerequisite=models.CharField(max_length=200)
    course_language=models.CharField(max_length=30)
    duration=models.IntegerField()
    fee=models.IntegerField(default=0)
    start_date=models.CharField(max_length=12)
    end_date=models.CharField(max_length=12)
    lock=models.CharField(max_length=1,default=0)
    hide=models.CharField(max_length=1,default=0)
    course_pic=models.FileField(default='abc.jpg')

    def __str__(self):
        return self.cname

class enrolldata(models.Model):
    student_id=models.ForeignKey(student)
    course_id=models.ForeignKey(course)
    join_date=models.CharField(max_length=200,default=str(datetime.datetime.now()))
    fee_status=models.CharField(max_length=1,default='n')
    course_progress=models.CharField(max_length=10,default='0')
    flag=models.CharField(max_length=1,default='0')
    progress_data=models.CharField(max_length=1000,default='')
    def __str__(self):
        return self.course_id.cname+'-'+self.student_id.uname


class coursecontent(models.Model):
    course_id = models.ForeignKey(course,on_delete=models.CASCADE)
    content_sub_id = models.IntegerField(default=0)
    content_name = models.CharField(max_length=50)
    content_description = models.CharField(max_length=500,default='description')
    content_type = models.CharField(default='null',max_length=10)
    content_url = models.FileField(default='abc.mp4')
    content_sequence_no = models.IntegerField(default=-1)
    def __str__(self):
        return self.content_name

class announcements(models.Model):
    course_id = models.ForeignKey(course,on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    Adate = models.CharField(max_length=50)
    Atime = models.CharField(max_length=50)
    def __str__ (self):
        return self.title

class resource_type(models.Model):
    name = models.CharField(max_length=10)
    def __str__ (self):
        return self.name

class resources1(models.Model):
    content_id = models.ForeignKey(coursecontent,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    type = models.ForeignKey(resource_type,on_delete=models.CASCADE)
    description = models.CharField(max_length=500,default='none')
    content_url1 = models.FileField(default='xyz.mp4')
    content_url2 = models.CharField(max_length=200,default='')
    sequence_no = models.IntegerField(default=-1)
    def __str__(self):
        return self.name + ":" +self.type.name

class difficulty_levels(models.Model):
    name = models.CharField(max_length=10)
    def __str__ (self):
        return self.name


class add_question(models.Model):
    course_id = models.ForeignKey(course,on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    question_type = models.CharField(max_length=20)
    answer = models.CharField(max_length=200)
    feedbackc = models.CharField(max_length=200)
    feedbackw = models.CharField(max_length=200)
    hint = models.CharField(max_length=200)
    difficulty = models.ForeignKey(difficulty_levels,on_delete=models.CASCADE)
    option1 = models.CharField(max_length=50,default=None,blank=True,null=True)
    option2 = models.CharField(max_length=50,default=None,blank=True,null=True)
    option3 = models.CharField(max_length=50,default=None,blank=True,null=True)
    option4 = models.CharField(max_length=50,default=None,blank=True,null=True)
    def __str__ (self):
        return self.question

class quiz(models.Model):
    content_id = models.ForeignKey(coursecontent,on_delete=models.CASCADE)
    instructor_id = models.ForeignKey(instructor,on_delete=models.CASCADE)
    question_id = models.CharField(max_length=400)
    quiz_title = models.CharField(max_length=50)
    quiz_description = models.CharField(max_length=500)
    quiz_duration = models.IntegerField()
    quiz_weightage = models.CharField(max_length=4)
    quiz_date = models.CharField(max_length=100)
    difficulty = models.ForeignKey(difficulty_levels,on_delete=models.CASCADE)
    lock = models.CharField(max_length=1)
    hide = models.CharField(max_length=1)
    def __str__ (self):
        return self.quiz_title

class faq(models.Model):
    course_id = models.ForeignKey(course, on_delete=models.CASCADE)
    faq_question = models.CharField(max_length=100)
    faq_answer = models.TextField()

    def __str__(self):
        return self.faq_question

class uploadcsv(models.Model):
    csvfile = models.FileField(default='abc.csv')


