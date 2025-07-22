from . import views
from django.urls import path

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('register/', views.register, name='register'),
    path('<str:username>/', views.chat_room, name='chat_room'),
]
