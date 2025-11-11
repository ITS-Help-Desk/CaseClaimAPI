from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_routes),
    path('login/', views.login),
    path('signup/', views.signup),
    path('test_token/', views.test_token),
    path('roles/', views.get_roles),
    path('users/', views.list_users),
    path('users/<int:pk>/edit_roles/', views.edit_user_roles),
]
