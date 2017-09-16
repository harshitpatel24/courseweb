from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from home import views

urlpatterns = [
  url(r'^$',views.home,name='home'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.UPLOAD_URL, documnet_root=settings.UPLOAD_ROOT)