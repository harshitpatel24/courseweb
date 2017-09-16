from django.conf.urls import url,include
from django.views.generic import ListView,DetailView

from blog import views
from blog.models import blog_post


urlpatterns=[
    url(r'^create/$',views.create,name='create'),
    url(r'^view_blog/$',views.view_blog,name='view_blog'),
    url(r'^visit_blog/+(?P<blog_id>\d+)/$',views.visit_blog,name='visit_blog'),
]