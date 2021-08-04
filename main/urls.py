from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('signup/', views.signup, name="signup"),
    path('login/', views.login, name="login"),
    path('recommend/<str:pk_test>', views.recommend, name="recommend"),
]
