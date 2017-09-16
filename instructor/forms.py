from django import forms
from django_summernote.widgets import SummernoteWidget

from instructor.models import add_question, faq
from student.models import askquestion


class add_questionForm(forms.ModelForm):
    question = forms.CharField(widget=SummernoteWidget(attrs={'width': '100%', 'height': '300px','placeholder':'Enter Question Here','required':'required'}))
    class Meta():
        model = add_question
        fields = ['question']
        widgets = {
            #'body': SummernoteInplaceWidget(),
            'question': SummernoteWidget(),
        }

class faq_Form(forms.ModelForm):
    faq_answer = forms.CharField(widget=SummernoteWidget(attrs={'height': '300px','placeholder':'Enter Answer Here',}))
    class Meta():
        model = faq
        fields = ['faq_answer']
        widgets = {
            #'body': SummernoteInplaceWidget(),
            'faq_answer': SummernoteWidget(),
        }