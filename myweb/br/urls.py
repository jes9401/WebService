from django.urls import path
from . import views


urlpatterns = [
    path('', views.br_home, name='home'),
    path('test/',views.test,name='test'),
    path('exercise1/',views.exercise1,name='exercise1'),
    path('exercise2/',views.exercise2,name='exercise2'),
    path('exercise3/',views.exercise3,name='exercise3'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('temp/',views.temp,name='temp'),
    path('temp/<exercise>/<username>/<postid>/',views.temp2,name='temp2'),
    path('getmlops/',views.getmlops,name='getmlops'),
]