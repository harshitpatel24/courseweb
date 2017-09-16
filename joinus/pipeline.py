import requests
from django.http import HttpResponseRedirect, request, HttpResponse
from django.shortcuts import render, render_to_response

from joinus.models import student

def save_profile(backend, response, *args, **kwargs):
    print(response.get('gender'))
    globals()['fname']=kwargs['details'].get('first_name')
    globals()['lname']=kwargs['details'].get('last_name')
    globals()['email']=kwargs['details'].get('email')
    globals()['uname']=kwargs['details'].get('username')
    print("exiting pipeline")
