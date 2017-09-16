from django.contrib import admin

# Register your models here
from django_summernote.admin import SummernoteModelAdmin
from forum.models import Forum, Topic, Post, ProfaneWord


class ForumAdmin(SummernoteModelAdmin):
    pass

class TopicAdmin(SummernoteModelAdmin):
    list_display = ["title", "forum", "creator", "created"]
    list_filter = ["forum", "creator"]

class PostAdmin(SummernoteModelAdmin):
    search_fields = ["title", "creator"]
    list_display = ["title", "topic", "creator", "created"]
    pass

class ProfaneWordAdmin(admin.ModelAdmin):
    pass

admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(ProfaneWord, ProfaneWordAdmin)
