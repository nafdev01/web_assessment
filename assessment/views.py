import subprocess

from django.contrib import messages
from django.shortcuts import redirect, render

from .assess import create_found_vulnerabilities, get_search_output
from .models import VulnAssessment


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


def view_results(request):
    assessments = VulnAssessment.objects.all()

    template_name = "assessment/results.html"
    context = {"assessments": assessments}
    return render(request, template_name, context)


def view_report(request, vuln_assessment_id):
    vuln_assessment = VulnAssessment.objects.get(id=vuln_assessment_id)

    template_name = "assessment/report.html"
    context = {"assessment": vuln_assessment}
    return render(request, template_name, context)
