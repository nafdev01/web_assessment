from django.contrib import admin

from .models import FoundVulnerability, VulnAssessment, Classification, ClassificationReference


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


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(ClassificationReference)
class ClassificationReferenceAdmin(admin.ModelAdmin):
    list_display = ("name", "reference_link", "classification")
    search_fields = ("name", "classification__name")
    list_filter = ("classification",)
