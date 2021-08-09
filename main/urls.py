from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('signup/', views.signup, name="signup"),
    path('login/', views.login, name="login"),
    path('recommend/<str:username>/', views.recommend, name="recommend"),
    path('not_loged_in/', views.not_loged_in, name='not_logged_in'),
    path('current-user/', views.current_user),
    path('user-create/', views.user_create),
    path('new_signup/', views.new_signup),
    path('new_vendor_signup/',views.new_vendor_signup),
]
