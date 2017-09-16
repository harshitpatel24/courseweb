from django import forms
from django_summernote.widgets import SummernoteWidget

from blog.models import blog_post


class post_descriptionForm(forms.ModelForm):
    post_description= forms.CharField(widget=SummernoteWidget(attrs={'width': '100%', 'height': '300px','placeholder':'Type Your Thoughts in 5000 words',}))
    class Meta():
        model = blog_post
        fields = ['post_description']
        widgets = {
            #'body': SummernoteInplaceWidget(),
            'post_description': SummernoteWidget(),
        }