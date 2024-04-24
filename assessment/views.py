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


@login_required
def assess_site(request):
    if request.method == "POST":
        form = AssessmentForm(data=request.POST)

        if form.is_valid():
            website = form.cleaned_data["url_here"]
            vuln_assessment = VulnAssessment.objects.create(
                client=request.user, website=website
            )

            detail_url = request.build_absolute_uri(vuln_assessment.get_absolute_url())

            conduct_assessment.delay(detail_url, vuln_assessment.id)
            return redirect("results_pending", assessment_id=vuln_assessment.id)
        else:
            messages.error(request, f"Form is invalid")
            return redirect("assess_site")

    template_name = "assessment/assess_site.html"
    context = {}
    return render(request, template_name, context)


@login_required
def results_pending(request, assessment_id):
    assessment = VulnAssessment.objects.get(id=assessment_id)

    if assessment.ready:
        messages.info(request, "Assessment is ready, these are the results")
        return redirect(assessment.get_absolute_url())

    template_name = "assessment/results_pending.html"
    context = {"assessment": assessment}
    return render(request, template_name, context)


@login_required
def view_results(request):
    assessments = VulnAssessment.objects.all()

    template_name = "assessment/results.html"
    context = {"assessments": assessments}
    return render(request, template_name, context)


@login_required
def view_report(request, vuln_assessment_id):
    vuln_assessment = VulnAssessment.objects.get(id=vuln_assessment_id)

    if not vuln_assessment.ready:
        messages.warning(
            request,
            "Assessment report is not ready yet, please wait",
        )
        return redirect("results_pending", assessment_id=vuln_assessment.id)

    template_name = "assessment/report.html"
    context = {"assessment": vuln_assessment}
    return render(request, template_name, context)


@login_required
def view_report_pdf(request, vuln_assessment_id):
    vuln_assessment = VulnAssessment.objects.get(id=vuln_assessment_id)
    assessed_on = vuln_assessment.tested_on.strftime("%B %d, %Y")

    template_name = "assessment/report-template.html"
    context = {"assessment": vuln_assessment}
    html_string = render_to_string(template_name, context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f"inline; filename={request.user.get_full_name()}'s Report for {vuln_assessment.website}.pdf"
    )
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), response)

    if not pdf.err:
        return response
    else:
        return HttpResponse("Error Rendering PDF", status=400)
