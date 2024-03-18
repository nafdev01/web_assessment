from django.urls import path

from . import views

urlpatterns = [
    path("", views.assess_site, name="assess_site"),
    path("results/", views.view_results, name="view_results"),
    path("results/<int:vuln_assessment_id>/", views.view_report, name="view_report"),
]
