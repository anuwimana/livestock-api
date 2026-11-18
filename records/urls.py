from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.Register.as_view()),
    path('animals/', views.AnimalListCreate.as_view()),
    path('animals/<int:pk>/', views.AnimalDetail.as_view()),
    path('treatments/', views.TreatmentListCreate.as_view()),
    path('treatments/<int:pk>/', views.TreatmentDetail.as_view()),
    path('analytics/treatments-per-species-month/', views.TreatmentAnalytics.as_view()),
]