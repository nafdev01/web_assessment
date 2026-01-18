from django.urls import path

from . import views

urlpatterns = [
    path("", views.assess_site, name="assess_site"),
    path(
        "submitted/<uuid:assessment_id>/", views.results_pending, name="results_pending"
    ),
    path("results/", views.view_results, name="view_results"),
    path("results/<uuid:vuln_assessment_id>/", views.view_report, name="view_report"),
    path(
        "results/pdf/<uuid:vuln_assessment_id>/",
        views.view_report_pdf,
        name="view_report_pdf",
    ),
]
