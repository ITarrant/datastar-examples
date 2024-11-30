from django.urls import path
from . import views

app_name = 'datastar'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('add_todos', views.add_todos, name='add_todo'),
    path('check_off_todo/<int:pk>/', views.check_off_todo, name='check_off_todo'),
    path('clear_todos/', views.clear_todos, name='clear_todos'),
]
