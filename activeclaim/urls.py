from django.urls import path
from . import views

urlpatterns = [
    path('create/<str:pk>/', views.create_active_claim),
    path('complete/<str:pk>/', views.complete_active_claim),
    path('list/', views.list_active_claims),
]