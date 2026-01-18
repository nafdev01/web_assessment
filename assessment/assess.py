import json
import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template

from .models import Classification, FoundVulnerability

logger = logging.getLogger(__name__)


def get_search_output(input_file):
    logger.info(f"Parsing vulnerabilities from {input_file}")
    
    try:
        # Read JSON data from input file
        with open(input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Input file {input_file} not found")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {input_file}: {e}")
        return []

    # Extract vulnerabilities section
    vulnerabilities = data.get("vulnerabilities", {})

    # Extract found vulnerabilities
    found_vulnerabilities = []
    for vulnerability, details in vulnerabilities.items():
        if details:
            for detail in details:
                entry = {"Vulnerability": vulnerability, **detail}
                if entry not in found_vulnerabilities:
                    found_vulnerabilities.append(entry)

    logger.info(f"Parsed {len(found_vulnerabilities)} unique vulnerabilities from {input_file}")
    return found_vulnerabilities


def create_found_vulnerabilities(assessment, vulnerabilities):
    logger.info(f"Creating {len(vulnerabilities)} vulnerability records for assessment {assessment.id}")
    
    # Create found vulnerabilities
    created_count = 0
    for vulnerability in vulnerabilities:
        try:
            found_vulnerability = FoundVulnerability(
                vuln_assessment=assessment,
                vulnerability_type=vulnerability["Vulnerability"],
                method=vulnerability["method"],
                path=vulnerability["path"],
                info=vulnerability["info"],
                level=vulnerability["level"],
                parameter=vulnerability["parameter"],
                http_request=vulnerability["http_request"],
                curl_command=vulnerability["curl_command"],
            )
            found_vulnerability.save()
            created_count += 1

            # Link the vulnerability to the appropriate classification
            classification_name = vulnerability["Vulnerability"]
            try:
                classification = Classification.objects.get(name=classification_name)
                found_vulnerability.classification.add(classification)
                logger.debug(f"Linked vulnerability to classification: {classification_name}")
            except Classification.DoesNotExist:
                logger.warning(f"No Classification found for name {classification_name}")
            except Exception as e:
                logger.error(f"Error linking classification to found vulnerability: {e}")
        except Exception as e:
            logger.error(f"Error creating vulnerability record: {e}")
    
    logger.info(f"Successfully created {created_count} vulnerability records for assessment {assessment.id}")


# def dummy_conduct_assessment(sender_email):
#     try:
#         send_feedback_email_task.delay(sender_email)
#         return True
#     except Exception as e:
#         # Log the error or handle it in a way appropriate for your application
#         print(f"An error occurred while sending the assessment email: {e}")
#         return False


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
