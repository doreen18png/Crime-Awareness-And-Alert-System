from django.contrib import admin
from .models import CrimeReport, ReportComment


@admin.register(CrimeReport)
class CrimeReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'severity', 'status', 'area', 'reporter', 'created_at')
    list_filter = ('category', 'severity', 'status')
    search_fields = ('title', 'description', 'address', 'area')
    readonly_fields = ('ai_summary', 'ai_risk_score', 'ai_recommendations', 'created_at', 'updated_at')
    list_editable = ('status',)


@admin.register(ReportComment)
class ReportCommentAdmin(admin.ModelAdmin):
    list_display = ('report', 'author', 'is_official', 'created_at')
    list_filter = ('is_official',)
