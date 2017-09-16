import datetime

from django.db import models

# Create your models here.
from joinus.models import student


class blog_post(models.Model):
    student_id=models.ForeignKey(student,on_delete=models.CASCADE)
    post_sub_id=models.CharField(max_length=10,default=0)
    blog_name=models.CharField(max_length=100)
    post_title=models.CharField(max_length=100)
    post_description=models.TextField(max_length=5000)
    date=models.CharField(max_length=15,default=str(datetime.datetime.now().strftime('%d/%m/%Y')))
    time=models.CharField(max_length=15,default=str(datetime.datetime.now().strftime('%H:%M')))
    count=models.CharField(max_length=15,default=0)
    def __str__(self):
        return self.title