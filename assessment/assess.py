import json
from .models import VulnAssessment, FoundVulnerability, Classification


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
