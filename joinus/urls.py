from django.conf.urls import url, include
from django.contrib import admin

from joinus import views

urlpatterns = [

    url(r'^register/$', views.register,name='register'),
    url(r'^login/$',views.login,name='login'),
    url(r'^signout/$',views.signout,name='login'),
    url(r'^demo/$',views.demo,name='demo'),
    url(r'^check/', views.checklogin, name='check'),
    url(r'^verify/(?P<user_id>\d+)+/$',views.verify,name='verify'),
    url(r'^sendagain/(?P<user_id>\d+)+/$',views.sendagain,name='sendagain'),
    url(r'^forgot/$',views.forgot,name='forgot'),
    url(r'^sendotpforgot/$',views.sendotpforgot,name='forgot'),
    url(r'^verify_forgot/(?P<user_id>\d+)+/$',views.verify_forgot,name='verify_forgot'),
    url(r'^sendagain_forgot/(?P<user_id>\d+)+/$',views.sendagain_forgot,name='sendagain_forgot'),
    url(r'^set_password/(?P<user_id>\d+)+/$',views.set_password,name='set_password'),
    url(r'^complete_profile/$', views.complete_profile, name='complete'),
]
