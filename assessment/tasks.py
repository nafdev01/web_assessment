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
    logger.info(f"Starting assessment task for assessment ID: {vuln_assessment_id}")
    
    try:
        vuln_assessment = VulnAssessment.objects.get(id=vuln_assessment_id)
    except VulnAssessment.DoesNotExist:
        logger.error(f"Assessment {vuln_assessment_id} not found in database")
        return

    logger.info(f"Running Wapiti scan for website: {vuln_assessment.website}")
    
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
        logger.info(f"Wapiti scan completed successfully for {vuln_assessment.website}")
        _search_output = result.stdout
    else:
        _search_output = "Command failed"
        logger.error(f"Wapiti command failed with return code {result.returncode}: {result.stderr}")

    try:
        vulnerabilities = get_search_output("feed.json")
        logger.info(f"Found {len(vulnerabilities)} vulnerabilities for assessment {vuln_assessment_id}")
    except Exception as e:
        logger.error(f"Error parsing vulnerabilities from feed.json: {e}")
        vulnerabilities = []

    # delete the feed file
    cleanup = subprocess.run(["rm", "feed.json"], capture_output=True, text=True)

    if cleanup.returncode != 0:
        logger.error(f"Error deleting feed.json file: {cleanup.stderr}")
    else:
        logger.debug(f"Successfully cleaned up feed.json file")

    try:
        create_found_vulnerabilities(vuln_assessment, vulnerabilities)
        logger.info(f"Successfully created vulnerability records for assessment {vuln_assessment_id}")
    except Exception as e:
        logger.error(f"Error creating vulnerability records: {e}")

    vuln_list = list()

    for vuln in vuln_assessment.vulnerabilities.all():
        vuln_list.append(
            f"{vuln.vulnerability_type}: ({vuln.info}) on {vuln_assessment.website}"
        )

    try:
        vuln_assessment.ready = True
        vuln_assessment.save()
        logger.info(f"Assessment {vuln_assessment_id} marked as ready")
        send_successful_assessment_email(detail_url, vuln_assessment)
        logger.info(f"Assessment completion email sent for {vuln_assessment_id}")
    except Exception as e:
        logger.error(f"Error sending email for assessment {vuln_assessment_id}: {e}")
