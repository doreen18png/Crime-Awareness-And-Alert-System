from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='list'),
    path('submit/', views.submit_report, name='submit'),
    path('mine/', views.my_reports, name='my_reports'),
    path('<int:pk>/', views.report_detail, name='detail'),
    path('api/geojson/', views.api_reports_geojson, name='geojson'),
]
