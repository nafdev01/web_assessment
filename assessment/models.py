from django.db import models
from django.utils import timezone


class VulnAssessment(models.Model):
    client = models.ForeignKey(
        "accounts.Client",
        on_delete=models.CASCADE,
        null=True,
        related_name="vuln_assessments",
    )
    website = models.CharField(max_length=100)
    tested_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.website

    class Meta:
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"
        ordering = ["-tested_on"]


class FoundVulnerability(models.Model):
    vuln_assessment = models.ForeignKey(
        VulnAssessment, on_delete=models.CASCADE, related_name="vulnerabilities"
    )
    vulnerability_type = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=255)
    info = models.TextField()
    level = models.IntegerField()
    parameter = models.CharField(max_length=255)
    http_request = models.TextField()
    curl_command = models.TextField()
    found_on = models.DateTimeField(default=timezone.now)
    classification = models.ManyToManyField("Classification", blank=True)

    def __str__(self):
        return (
            f"{self.vulnerability_type} ({self.info}) on {self.vuln_assessment.website}"
        )

    class Meta:
        verbose_name = "Found Vulnerability"
        verbose_name_plural = "Found Vulnerabilities"
        ordering = ["-found_on"]


class Classification(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    solution = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Classification"
        verbose_name_plural = "Classifications"
        ordering = ["name"]


class ClassificationReference(models.Model):
    classification = models.ForeignKey(
        Classification, on_delete=models.CASCADE, related_name="references"
    )
    name = models.CharField(max_length=255)
    reference_link = models.URLField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Classification Reference"
        verbose_name_plural = "Classification References"
        ordering = ["name"]
