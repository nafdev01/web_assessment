from django.contrib import admin
from .models import VulnAssessment, FoundVulnerability


@admin.register(VulnAssessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("website", "tested_on")
    search_fields = ("website",)
    list_filter = ("tested_on",)


@admin.register(FoundVulnerability)
class FoundVulnerabilityAdmin(admin.ModelAdmin):
    list_display = ("vulnerability_type", "info", "vuln_assessment", "level")
    search_fields = ("vulnerability_type", "vuln_assessment__website")
    list_filter = ("level",)
