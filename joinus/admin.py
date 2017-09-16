from django.contrib import admin

from .models import student,instructor


admin.site.register(student)
admin.site.register(instructor)