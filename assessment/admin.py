from django.contrib import admin

from .models import VulnAssessment


@admin.register(VulnAssessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("website", "tested_on")
    search_fields = ("website",)
    list_filter = ("tested_on",)
