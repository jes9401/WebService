from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'accounts'


urlpatterns = [
#    path('signup/', views.signup, name='signup'),
#    path('login/', views.login, name='login'),
#    path('logout/', views.logout, name='logout'),
    path('home/', views.home, name='home'),
    path('register/',views.register,name='register'),
    path('getUser/',views.getUser),
]