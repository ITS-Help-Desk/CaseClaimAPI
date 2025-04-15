from django.urls import path
from . import views

urlpatterns = [
    #path('', views.get_routes),
    path('list/', views.get_parent_cases),
    path('active/', views.get_active_parent_cases),
    path('set_inactive/<str:case_num>/', views.set_inactive_parent_case),
    path('create/', views.create_parent_case),
    path('update/<str:case_num>/', views.update_parent_case)
]