from django.urls import path
from . import views

app_name = 'emergency'

urlpatterns = [
    path('', views.sos_page, name='sos'),
    path('trigger/', views.trigger_sos, name='trigger'),
    path('alerts/', views.alert_list, name='alerts'),
    path('alerts/<int:pk>/', views.alert_detail, name='alert_detail'),
]
