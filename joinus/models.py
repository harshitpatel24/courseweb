from django.db import models

# Create your models here.

class student(models.Model):
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    uname = models.CharField(max_length=30)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=2000)
    pic = models.FileField()
    flag=models.CharField(max_length=2,default=1)

    def __str__(self):
        return self.fname + ' ' + self.lname

class instructor(models.Model):
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    uname = models.CharField(max_length=30)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=20)
    pic = models.FileField()

    def __str__(self):
        return self.email


class otp_generator(models.Model):
    student_id=models.ForeignKey(student)
    otp=models.CharField(max_length=6)