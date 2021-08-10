from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('login/', views.login, name="login"),
    path('recommend/<str:username>/', views.recommend, name="recommend"),
    path('not_loged_in/', views.not_loged_in, name='not_logged_in'),
    path('current-user/', views.current_user),
    path('user-create/', views.user_create),
    path('new_signup/', views.new_signup),
    path('new_vendor_signup/', views.new_vendor_signup),
    path('file_upload/', views.Mess_menu_upload),
    path('Closet_Value/', views.ClosestVendor),
    path('change_budget_spent/',views.Set_budget_spent),
    path('change_password/',ChangePasswordView.as_view()),
]