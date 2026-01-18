import json
import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template

logger = logging.getLogger(__name__)


def get_nuclei_output(results_file):
    """Parse vulnerabilities from nuclei JSON output file"""
    logger.info(f"Parsing vulnerabilities from nuclei results: {results_file}")
    
    try:
        # Read JSON data from nuclei results file
        with open(results_file, "r") as f:
            # Nuclei outputs JSONL (JSON Lines) format - one JSON object per line
            vulnerabilities = []
            for line in f:
                if line.strip():
                    try:
                        vuln_data = json.loads(line)
                        vulnerabilities.append(vuln_data)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error decoding JSON line: {e}")
                        continue
    except FileNotFoundError:
        logger.error(f"Nuclei results file {results_file} not found")
        return []
    except Exception as e:
        logger.error(f"Error reading nuclei results from {results_file}: {e}")
        return []

    logger.info(f"Parsed {len(vulnerabilities)} vulnerabilities from {results_file}")
    return vulnerabilities


def save_vuln_assessment_results(assessment, vulnerabilities):
    """Mark assessment as having results - vulnerability structure to be implemented later"""
    logger.info(f"Assessment {assessment.id} completed with {len(vulnerabilities)} vulnerabilities found")
    
    if not vulnerabilities:
        logger.info(f"No vulnerabilities found for assessment {assessment.id}")
    
    # Vulnerability storage structure will be implemented later
    # For now, just log the count
    logger.info(f"Nuclei results saved to: {assessment.nuclei_results_file.name if assessment.nuclei_results_file else 'N/A'}")


def send_successful_assessment_email(detail_url, vuln_assessment):
    logger.info(f"Preparing to send assessment completion email for {vuln_assessment.id}")

    # Retrieve entry by id
    subject = f"Assessment of Site {vuln_assessment.website} Completed!"
    sender = settings.EMAIL_HOST_USER
    recipient = f"{vuln_assessment.client.email}"
    
    logger.debug(f"Email details - From: {sender}, To: {recipient}, Subject: {subject}")
    
    try:
        message = get_template("assessment/assessment_email_template.html").render(
            {
                "detail_url": detail_url,
                "assessment": vuln_assessment,
            }
        )
        mail = EmailMessage(
            subject=subject,
            body=message,
            from_email=sender,
            to=[recipient],
            reply_to=[sender],
        )
        mail.content_subtype = "html"
        
        if mail.send():
            logger.info(f"Successfully sent assessment completion email to {recipient}")
            return True
        else:
            logger.error(f"Failed to send assessment completion email to {recipient}")
            return False
    except Exception as e:
        logger.error(f"Error sending assessment completion email: {e}")
        return False
