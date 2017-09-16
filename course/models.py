from django.db import models

# Create your models here.
from instructor.models import course, enrolldata, quiz, coursecontent
from joinus.models import student


class review(models.Model):
    student_id = models.ForeignKey(student,on_delete=models.CASCADE)
    course_id = models.ForeignKey(course, on_delete=models.CASCADE)
    rating=models.CharField(max_length=5)
    review=models.CharField(max_length=250)
    status=models.CharField(max_length=100,default='active')
    flag=models.CharField(max_length=2,default='n')
    def __str__(self):
        return self.course_id

class submissions(models.Model):
    quiz_id=models.ForeignKey(quiz)
    student_id=models.ForeignKey(student)
    percentage=models.FloatField(max_length=6)
    no_of_questions=models.CharField(max_length=3)
    submission_date=models.CharField(max_length=15)
    submission_time=models.CharField(max_length=15)


class course_progress(models.Model):
    student_id=models.ForeignKey(student)
    course_id= models.ForeignKey(course)
    course_main_content_id=models.IntegerField(default=0)
    course_sub_content_id=models.ForeignKey(coursecontent)
    status=models.CharField(max_length=3)
    def __str__(self):
        return self.course_id.cname


class certificate(models.Model):
    course_id=models.ForeignKey(course)
    student_id=models.ForeignKey(student)
    certificate_url=models.CharField(max_length=200)
    issue_date=models.CharField(max_length=15)
    scores_achieved=models.CharField(max_length=6)

