from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_routes),
    path('begin-review/<int:pk>/', views.begin_review),
    path('review/<int:pk>/', views.review_complete_claim),
    path('list/', views.list_complete_claims),
]