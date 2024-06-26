from django.urls import path

from . import views


app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('character/<int:id>/', views.character, name='character'),
    path('character/<int:id>/mail/', views.character_mail_list, name='character_mail_list'),
]
