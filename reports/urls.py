from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_routes),
    path('summary/', views.get_summary),
    path('user/<int:user_id>/', views.get_user_stats),
    path('leaderboard/', views.get_leaderboard),
    path('ping-stats/', views.get_ping_stats),
    path('date-range/', views.get_date_range_stats),
]

