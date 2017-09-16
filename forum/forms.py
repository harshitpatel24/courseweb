from functools import reduce

from django import forms

from coursewebsite.settings import DJANGO_SIMPLE_FORUM_FILTER_PROFANE_WORDS
from forum.models import ProfaneWord, Topic, Post
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

class TopicForm(forms.ModelForm):

    title = forms.CharField(max_length=60, required=True)

    class Meta():
        model = Topic
        exclude = ('creator','updated', 'created', 'closed', 'forum',)


class PostForm(forms.ModelForm):
    body = forms.CharField(widget=SummernoteWidget(attrs={'width': '100%', 'height': '300px','placeholder':'Enter Reply Here',}))
    class Meta():
        model = Post
        fields = ['body']
        widgets = {
            #'body': SummernoteInplaceWidget(),
            'body': SummernoteWidget(),
        }


