from django.urls import path

from . import views

app_name = 'boards'

urlpatterns = [
    path('', views.board_list, name='board_list'),
    path('<slug:slug>/', views.board_detail, name='board_detail'),
    path('<slug:board_slug>/<int:pk>/', views.thread_detail, name='thread_detail'),
]
