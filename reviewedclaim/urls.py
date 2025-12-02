from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_routes),
    path('getpings/<int:pk>/', views.get_pings_for_user),
    path('list/', views.list_reviewed_claims),
    path('acknowledge/<int:pk>/', views.acknowledge_ping),
    path('resolve/<int:pk>/', views.resolve_ping),
    path('create-ping/', views.create_manual_ping),
]
