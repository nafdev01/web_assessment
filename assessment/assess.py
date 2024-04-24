import json
import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template

from .models import Classification, FoundVulnerability

logger = logging.getLogger(__name__)


def get_search_output(input_file):
    # Read JSON data from input file
    with open(input_file, "r") as f:
        data = json.load(f)

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

    return found_vulnerabilities


def create_found_vulnerabilities(assessment, vulnerabilities):
    # Create found vulnerabilities
    for vulnerability in vulnerabilities:
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

        # Link the vulnerability to the appropriate classification
        classification_name = vulnerability["Vulnerability"]
        try:
            classification = Classification.objects.get(name=classification_name)
            found_vulnerability.classification.add(classification)
        except Classification.DoesNotExist:
            print(f"No Classification found for name {classification_name}")
        except Exception as e:
            print(f"Error linking classification to found vulnerability: {e}")


# def dummy_conduct_assessment(sender_email):
#     try:
#         send_feedback_email_task.delay(sender_email)
#         return True
#     except Exception as e:
#         # Log the error or handle it in a way appropriate for your application
#         print(f"An error occurred while sending the assessment email: {e}")
#         return False


def send_successful_assessment_email(detail_url, vuln_assessment):

    # Retrieve entry by id
    subject = f"Assessment of Site {vuln_assessment.website} Completed!"
    sender = settings.EMAIL_HOST_USER
    recipient = f"{vuln_assessment.client.email}"
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
        return True
    else:
        return False
