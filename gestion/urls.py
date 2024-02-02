from django.urls import path, include
from . import views

from django.contrib.auth.views import LoginView,LogoutView

urlpatterns = [
    path("", views.inicio, name='inicio'),

    #URLS para inicio de sesion
    path("login/", LoginView.as_view(template_name='gestion/login.html', redirect_authenticated_user=True), name='login'), #Mirar el radirect_authenticated_user
    path("logout/", LogoutView.as_view(), name='logout'), 

    #URL para el registro de usuario
    path("registro/", views.registro, name='registro'),

    path("my/", include("personal.urls")),

    path("html", views.html, name='html'),
]