import logging
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import get_template, render_to_string
from django.views.decorators.csrf import csrf_exempt
from xhtml2pdf import pisa

from .forms import AssessmentForm
from .models import VulnAssessment
from .tasks import conduct_assessment

logger = logging.getLogger(__name__)


@login_required
def assess_site(request):
    if request.method == "POST":
        form = AssessmentForm(data=request.POST)

        if form.is_valid():
            website = form.cleaned_data["url_here"]
            logger.info(f"User {request.user.username} initiated assessment for website: {website}")
            
            vuln_assessment = VulnAssessment.objects.create(
                client=request.user, website=website
            )

            detail_url = request.build_absolute_uri(vuln_assessment.get_absolute_url())

            logger.info(f"Created assessment {vuln_assessment.id} for {website}, triggering Celery task")
            conduct_assessment.delay(detail_url, vuln_assessment.id)
            return redirect("results_pending", assessment_id=vuln_assessment.id)
        else:
            logger.warning(f"Invalid assessment form submission by {request.user.username}: {form.errors}")
            messages.error(request, f"Form is invalid")
            return redirect("assess_site")

    template_name = "assessment/assess_site.html"
    context = {}
    return render(request, template_name, context)


@login_required
def results_pending(request, assessment_id):
    try:
        assessment = VulnAssessment.objects.get(id=assessment_id)
    except VulnAssessment.DoesNotExist:
        logger.error(f"User {request.user.username} attempted to access non-existent assessment {assessment_id}")
        messages.error(request, "Assessment not found")
        return redirect("view_results")

    if assessment.ready:
        logger.info(f"Assessment {assessment_id} is ready, redirecting to results")
        messages.info(request, "Assessment is ready, these are the results")
        return redirect(assessment.get_absolute_url())

    template_name = "assessment/results_pending.html"
    context = {"assessment": assessment}
    return render(request, template_name, context)


@login_required
def view_results(request):
    assessments = VulnAssessment.objects.all()
    logger.info(f"User {request.user.username} viewing results page with {assessments.count()} assessments")

    template_name = "assessment/results.html"
    context = {"assessments": assessments}
    return render(request, template_name, context)


@login_required
def view_report(request, vuln_assessment_id):
    try:
        vuln_assessment = VulnAssessment.objects.get(id=vuln_assessment_id)
    except VulnAssessment.DoesNotExist:
        logger.error(f"User {request.user.username} attempted to view non-existent report {vuln_assessment_id}")
        messages.error(request, "Assessment not found")
        return redirect("view_results")

    if not vuln_assessment.ready:
        logger.warning(f"User {request.user.username} attempted to view unready report {vuln_assessment_id}")
        messages.warning(
            request,
            "Assessment report is not ready yet, please wait",
        )
        return redirect("results_pending", assessment_id=vuln_assessment.id)

    logger.info(f"User {request.user.username} viewing report for assessment {vuln_assessment_id}")
    template_name = "assessment/report.html"
    context = {"assessment": vuln_assessment}
    return render(request, template_name, context)


@login_required
def view_report_pdf(request, vuln_assessment_id):
    try:
        vuln_assessment = VulnAssessment.objects.get(id=vuln_assessment_id)
    except VulnAssessment.DoesNotExist:
        logger.error(f"User {request.user.username} attempted to generate PDF for non-existent assessment {vuln_assessment_id}")
        messages.error(request, "Assessment not found")
        return redirect("view_results")
    
    assessed_on = vuln_assessment.tested_on.strftime("%B %d, %Y")
    logger.info(f"User {request.user.username} generating PDF report for assessment {vuln_assessment_id}")

    template_name = "assessment/report-template.html"
    context = {"assessment": vuln_assessment}
    html_string = render_to_string(template_name, context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f"inline; filename={request.user.get_full_name()}'s Report for {vuln_assessment.website}.pdf"
    )
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), response)

    if not pdf.err:
        logger.info(f"Successfully generated PDF for assessment {vuln_assessment_id}")
        return response
    else:
        logger.error(f"Error rendering PDF for assessment {vuln_assessment_id}: {pdf.err}")
        return HttpResponse("Error Rendering PDF", status=400)
