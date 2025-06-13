from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_routes),
    path('begin-review/<str:pk>/', views.begin_review),
    path('review/<str:pk>/', views.review_complete_claim),
    path('list/', views.list_complete_claims),
]