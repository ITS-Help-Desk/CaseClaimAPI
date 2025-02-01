from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.list_reviewed_claims),
]