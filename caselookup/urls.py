from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_routes),
    path('search/<str:casenum>/', views.search_case),
    path('history/<str:casenum>/', views.get_case_history),
    path('status/<str:casenum>/', views.get_case_status),
]

