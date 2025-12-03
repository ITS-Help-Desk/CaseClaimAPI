from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_routes),
    path('create/', views.create_evaluation),
    path('list/', views.list_evaluations),
    path('user/<int:user_id>/', views.get_user_evaluations),
    path('detail/<int:pk>/', views.get_evaluation_detail),
    path('update/<int:pk>/', views.update_evaluation),
    path('delete/<int:pk>/', views.delete_evaluation),
    path('generate/<int:user_id>/', views.generate_evaluation_data),
    path('geneval/', views.geneval),  # Auto-generate evaluations ZIP
]

