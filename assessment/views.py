import subprocess
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import get_template, render_to_string
from django.views.decorators.csrf import csrf_exempt
from xhtml2pdf import pisa

from .assess import create_found_vulnerabilities, get_search_output
from .models import VulnAssessment


@login_required
def assess_site(request):
    if request.method == "POST":
        website = request.POST["url-here"]

        command = [
            "wapiti",
            "-u",
            f"{website}",
            "-o",
            "feed.json",
            "--format",
            "json",
            "--format",
            "json",
            "--flush-session",
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            search_output = result.stdout
        else:
            search_output = "Command failed"
            messages.error(request, f"Command failed with error: {result.stderr}")
            return redirect("home")

        vulnerabilities = get_search_output("feed.json")

        # delete the feed file
        subprocess.run(["rm", "feed.json"])

        vuln_assessment = VulnAssessment(client=request.user, website=website)
        vuln_assessment.save()

        create_found_vulnerabilities(vuln_assessment, vulnerabilities)

        messages.success(
            request,
            f"Your vulnerablity assessment for {website} was successful! {len(vulnerabilities)} vulnerabilities found.",
        )
        return redirect("view_report", vuln_assessment_id=vuln_assessment.id)

    template_name = "assessment/assess_site.html"
    context = {}
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
