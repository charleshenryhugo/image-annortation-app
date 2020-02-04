from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path(r'test/', views.test_view),
    path(r'task/register/upload/', views.task_upload),
    path(r'task/', views.task_get),
    path(r'task/download/', views.task_download),
    path(r'image/', views.image_update)
]