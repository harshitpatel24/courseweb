from django import forms
from django_summernote.widgets import SummernoteWidget

from student.models import askquestion


class askquestionForm(forms.ModelForm):
    question_description = forms.CharField(widget=SummernoteWidget(attrs={'width': '100%', 'height': '300px','placeholder':'Enter Text Here',}))
    class Meta():
        model = askquestion
        fields = ['question_description']
        widgets = {
            #'body': SummernoteInplaceWidget(),
            'question_description': SummernoteWidget(),
        }