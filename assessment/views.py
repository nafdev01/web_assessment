import logging
import json
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
            logger.info(
                f"User {request.user.username} initiated assessment for website: {website}"
            )

            vuln_assessment = VulnAssessment.objects.create(
                client=request.user, website=website
            )

            detail_url = request.build_absolute_uri(vuln_assessment.get_absolute_url())

            logger.info(
                f"Created assessment {vuln_assessment.id} for {website}, triggering Celery task"
            )
            conduct_assessment.delay(detail_url, vuln_assessment.id)
            return redirect("results_pending", assessment_id=vuln_assessment.id)
        else:
            logger.warning(
                f"Invalid assessment form submission by {request.user.username}: {form.errors}"
            )
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
        logger.error(
            f"User {request.user.username} attempted to access non-existent assessment {assessment_id}"
        )
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
    logger.info(
        f"User {request.user.username} viewing results page with {assessments.count()} assessments"
    )

    template_name = "assessment/results.html"
    context = {"assessments": assessments}
    return render(request, template_name, context)


@login_required
def view_report(request, vuln_assessment_id):
    try:
        vuln_assessment = VulnAssessment.objects.get(id=vuln_assessment_id)
    except VulnAssessment.DoesNotExist:
        logger.error(
            f"User {request.user.username} attempted to view non-existent report {vuln_assessment_id}"
        )
        messages.error(request, "Assessment not found")
        return redirect("view_results")

    if not vuln_assessment.ready:
        logger.warning(
            f"User {request.user.username} attempted to view unready report {vuln_assessment_id}"
        )
        messages.warning(
            request,
            "Assessment report is not ready yet, please wait",
        )
        return redirect("results_pending", assessment_id=vuln_assessment.id)

    logger.info(
        f"User {request.user.username} viewing report for assessment {vuln_assessment_id}"
    )

    nuclei_logs = []
    stats = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0,
        "total": 0,
    }

    if vuln_assessment.nuclei_results_file:
        try:
            vuln_assessment.nuclei_results_file.open("rb")
            content = vuln_assessment.nuclei_results_file.read().decode(
                "utf-8", errors="replace"
            )

            # Try parsing as a single JSON array first (Nuclei JSON export)
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    nuclei_logs = data
                else:
                    nuclei_logs = [data]
            except json.JSONDecodeError:
                # Fallback to JSONL (line by line)
                nuclei_logs = []
                for line in content.splitlines():
                    if line.strip():
                        try:
                            log_entry = json.loads(line)
                            nuclei_logs.append(log_entry)
                        except json.JSONDecodeError:
                            continue

            # Normalize keys for Django templates (replace hyphens with underscores)
            def normalize_keys(obj):
                if isinstance(obj, dict):
                    return {
                        k.replace("-", "_"): normalize_keys(v) for k, v in obj.items()
                    }
                elif isinstance(obj, list):
                    return [normalize_keys(i) for i in obj]
                else:
                    return obj

            nuclei_logs = normalize_keys(nuclei_logs)

            # Calculate Stats (using normalized keys)
            for log_entry in nuclei_logs:
                severity = log_entry.get("info", {}).get("severity", "info").lower()
                if severity in stats:
                    stats[severity] += 1
                else:
                    stats["info"] += 1
                stats["total"] += 1

            # Extract all tags for the filter dropdown (before filtering)
            all_tags = set()
            for log in nuclei_logs:
                tags = log.get("info", {}).get("tags", [])
                if isinstance(tags, list):
                    for tag in tags:
                        all_tags.add(tag)

            # Sort tags for display
            all_tags = sorted(list(all_tags))

            # Filter by tag if requested
            tag_filter = request.GET.get("tag")
            if tag_filter:
                filtered_logs = []
                tag_filter_lower = tag_filter.lower()
                for log in nuclei_logs:
                    tags = log.get("info", {}).get("tags", [])
                    if isinstance(tags, list):
                        for tag in tags:
                            if tag_filter_lower in str(tag).lower():
                                filtered_logs.append(log)
                                break
                nuclei_logs = filtered_logs

            # Filter by search query if requested
            search_query = request.GET.get("search")
            if search_query:
                search_query_lower = search_query.lower()
                filtered_logs = []
                for log in nuclei_logs:
                    # Check text fields
                    name = log.get("info", {}).get("name", "").lower()
                    template_id = log.get("template_id", "").lower()
                    description = log.get("info", {}).get("description", "").lower()

                    if (
                        search_query_lower in name
                        or search_query_lower in template_id
                        or search_query_lower in description
                    ):
                        filtered_logs.append(log)
                nuclei_logs = filtered_logs

            vuln_assessment.nuclei_results_file.close()
        except Exception as e:
            logger.error(
                f"Error reading results file for assessment {vuln_assessment.id}: {e}"
            )
            tag_filter = None
            search_query = None
            all_tags = []

    template_name = "assessment/report.html"
    context = {
        "assessment": vuln_assessment,
        "nuclei_logs": nuclei_logs,
        "stats": stats,
        "tag_filter": tag_filter,
        "search_query": search_query,
        "all_tags": all_tags,
    }
    return render(request, template_name, context)


@login_required
def view_report_pdf(request, vuln_assessment_id):
    try:
        vuln_assessment = VulnAssessment.objects.get(id=vuln_assessment_id)
    except VulnAssessment.DoesNotExist:
        logger.error(
            f"User {request.user.username} attempted to generate PDF for non-existent assessment {vuln_assessment_id}"
        )
        messages.error(request, "Assessment not found")
        return redirect("view_results")

    assessed_on = vuln_assessment.tested_on.strftime("%B %d, %Y")
    logger.info(
        f"User {request.user.username} generating PDF report for assessment {vuln_assessment_id}"
    )

    # --- START: Load and Parse Nuclei Logs (Same logic as view_report) ---
    nuclei_logs = []
    if vuln_assessment.nuclei_results_file:
        try:
            vuln_assessment.nuclei_results_file.open("rb")
            content = vuln_assessment.nuclei_results_file.read().decode(
                "utf-8", errors="replace"
            )

            # Try parsing as a single JSON array first (Nuclei JSON export)
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    nuclei_logs = data
                else:
                    nuclei_logs = [data]
            except json.JSONDecodeError:
                # Fallback to JSONL (line by line)
                nuclei_logs = []
                for line in content.splitlines():
                    if line.strip():
                        try:
                            log_entry = json.loads(line)
                            nuclei_logs.append(log_entry)
                        except json.JSONDecodeError:
                            continue

            # Normalize keys for Django templates (replace hyphens with underscores)
            def normalize_keys(obj):
                if isinstance(obj, dict):
                    return {
                        k.replace("-", "_"): normalize_keys(v) for k, v in obj.items()
                    }
                elif isinstance(obj, list):
                    return [normalize_keys(i) for i in obj]
                else:
                    return obj

            nuclei_logs = normalize_keys(nuclei_logs)
            vuln_assessment.nuclei_results_file.close()

        except Exception as e:
            logger.error(
                f"Error reading results file for assessment {vuln_assessment.id} PDF generation: {e}"
            )
            nuclei_logs = []  # Ensure it's empty on error
    # --- END: Load and Parse Nuclei Logs ---

    template_name = "assessment/report-template.html"
    # Pass nuclei_logs instead of relying on assessment.vulnerabilities
    context = {"assessment": vuln_assessment, "nuclei_logs": nuclei_logs}
    html_string = render_to_string(template_name, context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f"inline; filename={request.user.get_full_name()}'s Report for {vuln_assessment.website}.pdf"
    )
    # xhtml2pdf handles CSS better if we link resources properly, but for now we rely on inline/CDN
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), response)

    if not pdf.err:
        logger.info(f"Successfully generated PDF for assessment {vuln_assessment_id}")
        return response
    else:
        logger.error(
            f"Error rendering PDF for assessment {vuln_assessment_id}: {pdf.err}"
        )
        return HttpResponse("Error Rendering PDF", status=400)
