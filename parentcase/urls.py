from django.urls import path
from . import views

urlpatterns = [
    #path('', views.get_routes),
    path('active', views.get_active_parent_cases),
    path('create', views.create_parent_case),
]