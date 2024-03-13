from django.shortcuts import render, redirect
from django.contrib import messages
from .models import VulnAssessment
import subprocess
from .assess import create_found_vulnerabilities, get_search_output


def home(request):
    if request.method == "POST":
        website = request.POST["url-here"]

        # Run your terminal command here
        # use this format wapiti -u https://eserver.kabarak.ac.ke -o feed.json --format json
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

        vuln_assessment = VulnAssessment(website=website, search_output=vulnerabilities)
        vuln_assessment.save()

        create_found_vulnerabilities(vuln_assessment, vulnerabilities)

        messages.success(
            request,
            f"Your vulnerablity assessment for {website} was successful!. {len(vulnerabilities)} vulnerabilities found.",
        )
        return redirect("home")

    template_name = "home.html"
    context = {}
    return render(request, template_name, context)


def view_results(request):
    assessments = VulnAssessment.objects.all()

    template_name = "results.html"
    context = {"assessments": assessments}
    return render(request, template_name, context)
from django.shortcuts import render

# Create your views here.
