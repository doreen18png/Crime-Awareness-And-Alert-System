from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

path('logout/', auth_views.LogoutView.as_view(), name='logout'),

# Customize admin panel branding
admin.site.site_header = "Vigilant Administration"
admin.site.site_title = "Vigilant Admin"
admin.site.index_title = "Crime Awareness & Alert System — Control Panel"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('reports/', include('reports.urls')),
    path('emergency/', include('emergency.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('auth/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
