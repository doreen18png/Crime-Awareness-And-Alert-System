from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('ai-insights/', views.ai_insights, name='ai_insights'),
]
