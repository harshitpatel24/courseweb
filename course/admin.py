from django.contrib import admin

# Register your models here.
from course.models import review, course_progress, certificate, submissions

admin.site.register(course_progress)
admin.site.register(certificate)
admin.site.register(submissions)