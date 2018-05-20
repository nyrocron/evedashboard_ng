from django.urls import path

from . import views

app_name = 'eveauth'

urlpatterns = [
    path('', views.index),
    path('sso-callback/', views.sso_callback, name='sso_callback'),
    path('characters/', views.character_list, name='char_list'),
    path('characters/add/', views.character_add, name='char_add'),
    path('characters/delete/<int:token_id>/', views.character_delete, name='char_del'),
]
