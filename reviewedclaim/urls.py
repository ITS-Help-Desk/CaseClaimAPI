from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_routes),
    path('getpings/<int:pk>/', views.get_pings_for_user),
    path('list/', views.list_reviewed_claims),
]