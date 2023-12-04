from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_content, name='add_content'),
    path('list/', views.list_episodes, name='content_list'),
]