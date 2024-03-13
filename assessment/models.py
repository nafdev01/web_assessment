from django.db import models

from django.db import models
from django.utils import timezone


# Create your models here.
class VulnAssessment(models.Model):
    website = models.CharField(max_length=100)
    tested_on = models.DateTimeField(default=timezone.now)
    search_output = models.TextField()

    def __str__(self):
        return self.website

    class Meta:
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"
        ordering = ["-tested_on"]


class FoundVulnerability(models.Model):
    vuln_assessment = models.ForeignKey(VulnAssessment, on_delete=models.CASCADE)
    vulnerability_type = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=255)
    info = models.TextField()
    level = models.IntegerField()
    parameter = models.CharField(max_length=255)
    http_request = models.TextField()
    curl_command = models.TextField()
    found_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.vulnerability_type} ({self.info}) on {self.vuln_assessment.website}"

    class Meta:
        verbose_name = "Found Vulnerability"
        verbose_name_plural = "Found Vulnerabilities"
        ordering = ["-found_on"]
