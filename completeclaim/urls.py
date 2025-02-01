from django.urls import path
from . import views

urlpatterns = [
    path('review/<str:pk>/', views.review_complete_claim),
    path('list/', views.list_complete_claims),
]