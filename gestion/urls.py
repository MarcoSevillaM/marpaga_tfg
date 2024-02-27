from django.urls import path, include
from . import views

from django.contrib.auth.views import LoginView,LogoutView
from .views import CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
#Cuando el usuario ha olvidado la constraseña
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.inicio, name='inicio'),

    #URLS para inicio de sesion
    path("login/", LoginView.as_view(template_name='gestion/login.html', redirect_authenticated_user=True), name='login'), #Mirar el radirect_authenticated_user
    path("logout/", LogoutView.as_view(), name='logout'), 

    #URL para el registro de usuario
    path("registro/", views.registro, name='registro'),
    path("activate/<uidb64>/<token>/", views.activate, name='activate'),

    path("my/", include("personal.urls")),

    #URLS para el cambio de contraseña
    #path('password_reset/', auth_views.PasswordResetView.as_view(template_name='gestion/reset_passwd.html'), name='password_reset'),
    #path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    #path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    #path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('password_reset/', CustomPasswordResetView.as_view(template_name='gestion/reset_passwd.html'), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(template_name='gestion/reset_passwd.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(template_name='gestion/reset_passwd_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(template_name='gestion/reset_passwd_confirm.html'), name='password_reset_complete'),


]