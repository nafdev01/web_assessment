import logging
import subprocess

from celery import shared_task

from assessment.assess import (
    create_found_vulnerabilities,
    get_search_output,
    send_successful_assessment_email,
)
from assessment.models import VulnAssessment

logger = logging.getLogger(__name__)


@shared_task
def conduct_assessment(detail_url, vuln_assessment_id):
    vuln_assessment = VulnAssessment.objects.get(id=vuln_assessment_id)

    command = [
        "wapiti",
        "-u",
        f"{vuln_assessment.website}",
        "-o",
        "feed.json",
        "--format",
        "json",
        "--format",
        "json",
        "--flush-session",
        "-m",
        "backup,cookieflags,crlf,csp,csrf,htaccess,http_headers,methods,nikto,redirect,xss,xxe",
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    # Check if the command was successful
    if result.returncode == 0:
        _search_output = result.stdout
    else:
        _search_output = "Command failed"
        logger.error(f"Command failed with error: {result.stderr}")

    vulnerabilities = get_search_output("feed.json")

    # delete the feed file
    cleanup = subprocess.run(["rm", "feed.json"], capture_output=True, text=True)

    if cleanup.returncode != 0:
        logger.error(f"Error deleting feed.json file: {cleanup.stderr}")

    create_found_vulnerabilities(vuln_assessment, vulnerabilities)

    vuln_list = list()

    for vuln in vuln_assessment.vulnerabilities.all():
        vuln_list.append(
            f"{vuln.vulnerability_type}: ({vuln.info}) on {vuln_assessment.website}"
        )

    try:
        vuln_assessment.ready = True
        vuln_assessment.save()
        send_successful_assessment_email(detail_url, vuln_assessment)
    except Exception as e:
        logger.error(f"Error sending email: {e}")
