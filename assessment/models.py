import os
import uuid
from django.core.files import File
from django.db import models
from django.urls import reverse
from django.utils import timezone


class VulnAssessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        "accounts.Client",
        on_delete=models.CASCADE,
        null=True,
        related_name="vuln_assessments",
    )
    website = models.CharField(max_length=100)
    ready = models.BooleanField(default=False)
    tested_on = models.DateTimeField(default=timezone.now)
    nuclei_results_file = models.FileField(
        upload_to="nuclei_results/", null=True, blank=True
    )

    def __str__(self):
        return self.website

    def get_absolute_url(self):
        return reverse("view_report", kwargs={"vuln_assessment_id": self.id})

    def get_temp_results_path(self):
        """Get temporary file path for nuclei results"""
        return f"/tmp/nuclei_results_{self.id}.jsonl"

    def save_results_from_temp(self, temp_path):
        """Copy results from temp file to media folder"""
        try:
            if os.path.exists(temp_path):
                with open(temp_path, "rb") as f:
                    filename = f"nuclei_results_{self.id}.jsonl"
                    self.nuclei_results_file.save(filename, File(f), save=True)
                # Clean up temp file
                os.remove(temp_path)
                return True
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error saving results from temp: {e}")
        return False

    class Meta:
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"
        ordering = ["-tested_on"]
