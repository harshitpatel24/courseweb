from django.contrib import admin
from .models import quiz, course, enrolldata, coursecontent, announcements, difficulty_levels, add_question, resources1, resource_type, \
    faq, categories

# Register your models here.

admin.site.register(course)
admin.site.register(enrolldata)
admin.site.register(coursecontent)
admin.site.register(announcements)
admin.site.register(difficulty_levels)
admin.site.register(add_question)
admin.site.register(quiz)
admin.site.register(resources1)
admin.site.register(resource_type)
admin.site.register(faq)
admin.site.register(categories)