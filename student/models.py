import datetime

from django.db import models

# Create your models here.
from instructor.models import course
from joinus.models import student, instructor

class askquestion(models.Model):
    student_id=models.ForeignKey(student,on_delete=models.CASCADE)
    course_id=models.ForeignKey(course,on_delete=models.CASCADE)
    instructor_id=models.ForeignKey(instructor,on_delete=models.CASCADE)
    question_subid=models.IntegerField(default=0)
    question_heading=models.CharField(max_length=100)
    question_description=models.TextField(max_length=250)
    reply_description=models.CharField(max_length=250)
    sequence_no=models.CharField(max_length=5)
    question_date=models.CharField(max_length=20,default=datetime.datetime.now().strftime ("%d/%m/%Y"))
    question_time = models.CharField(max_length=20,default=datetime.datetime.now().strftime ("%H:%M"))
    reply_date=models.CharField(max_length=20,default=datetime.datetime.now().strftime ("%d/%m/%Y"))
    reply_time=models.CharField(max_length=20,default=datetime.datetime.now().strftime ("%H:%M"))
    question_flag=models.CharField(max_length=1,default='y')
    reply_flag=models.CharField(max_length=1,default='n')
