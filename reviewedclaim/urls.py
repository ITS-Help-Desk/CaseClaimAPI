from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_routes),
    path('list/', views.list_reviewed_claims),
]