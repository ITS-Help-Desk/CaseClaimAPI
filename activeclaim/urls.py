from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_routes),
    path('create/<str:pk>/', views.create_active_claim),
    path('complete/<str:pk>/', views.complete_active_claim),
    path('unclaim/<str:pk>/', views.unclaim_active_claim),
    path('list/', views.list_active_claims),
]