from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_routes),
    path('login/', views.login),
    path('signup/', views.signup),
    path('test_token/', views.test_token),
]
