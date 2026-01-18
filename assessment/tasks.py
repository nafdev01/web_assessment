import logging
import subprocess
import os

from celery import shared_task

from assessment.assess import (
    get_nuclei_output,
    save_vuln_assessment_results,
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

    # Get temporary file path for nuclei to save results
    temp_results_path = vuln_assessment.get_temp_results_path()
    logger.info(f"Running Nuclei scan for website: {vuln_assessment.website}")
    logger.info(f"Temporary results path: {temp_results_path}")
    
    # Run nuclei command - saves to temp file first
    command = [
        "nuclei",
        "-u",
        vuln_assessment.website,
        "-je",
        temp_results_path,
    ]

    logger.info(f"Executing command: {' '.join(command)}")
    
    # Run nuclei with real-time output streaming
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Stream stdout in real-time
    for line in process.stdout:
        if line.strip():
            logger.info(f"Nuclei: {line.strip()}")
    
    # Wait for process to complete and get return code
    return_code = process.wait()
    
    # Capture any stderr output
    stderr_output = process.stderr.read()
    
    # Check if the command was successful
    if return_code == 0:
        logger.info(f"Nuclei scan completed successfully for {vuln_assessment.website}")
    else:
        logger.warning(f"Nuclei command completed with return code {return_code}")
        if stderr_output:
            logger.debug(f"Nuclei stderr: {stderr_output}")

    # Verify the temp file was created
    if os.path.exists(temp_results_path):
        logger.info(f"Nuclei temp results file created: {temp_results_path}")
        file_size = os.path.getsize(temp_results_path)
        logger.info(f"Temp file size: {file_size} bytes")
        
        # Copy from temp to media folder using FileField
        if vuln_assessment.save_results_from_temp(temp_results_path):
            logger.info(f"Results copied to media folder: {vuln_assessment.nuclei_results_file.name}")
            
            # Get the final file path for parsing
            final_results_path = vuln_assessment.nuclei_results_file.path
            logger.info(f"Final results path: {final_results_path}")
        else:
            logger.error(f"Failed to copy results from temp to media folder")
            return
    else:
        logger.error(f"Nuclei temp results file was not created: {temp_results_path}")
        return

    # Parse vulnerabilities from the saved file
    try:
        vulnerabilities = get_nuclei_output(final_results_path)
        logger.info(f"Found {len(vulnerabilities)} vulnerabilities for assessment {vuln_assessment_id}")
    except Exception as e:
        logger.error(f"Error parsing vulnerabilities from {final_results_path}: {e}")
        vulnerabilities = []

    # Save vulnerability results to the assessment
    try:
        save_vuln_assessment_results(vuln_assessment, vulnerabilities)
        logger.info(f"Successfully processed vulnerability results for assessment {vuln_assessment_id}")
    except Exception as e:
        logger.error(f"Error saving vulnerability results: {e}")

    # Mark assessment as ready and send email
    try:
        vuln_assessment.ready = True
        vuln_assessment.save()
        logger.info(f"Assessment {vuln_assessment_id} marked as ready")
        send_successful_assessment_email(detail_url, vuln_assessment)
        logger.info(f"Assessment completion email sent for {vuln_assessment_id}")
    except Exception as e:
        logger.error(f"Error sending email for assessment {vuln_assessment_id}: {e}")
