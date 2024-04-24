# Generated by Django 5.0.3 on 2024-03-13 15:44

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="VulnAssessment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("website", models.CharField(max_length=100)),
                ("tested_on", models.DateTimeField(default=django.utils.timezone.now)),
                ("search_output", models.TextField()),
            ],
            options={
                "verbose_name": "Assessment",
                "verbose_name_plural": "Assessments",
                "ordering": ["-tested_on"],
            },
        ),
        migrations.CreateModel(
            name="FoundVulnerability",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("vulnerability_type", models.CharField(max_length=255)),
                ("method", models.CharField(max_length=10)),
                ("path", models.CharField(max_length=255)),
                ("info", models.TextField()),
                ("level", models.IntegerField()),
                ("parameter", models.CharField(max_length=255)),
                ("http_request", models.TextField()),
                ("curl_command", models.TextField()),
                ("found_on", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "vuln_assessment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="assessment.vulnassessment",
                    ),
                ),
            ],
            options={
                "verbose_name": "Found Vulnerability",
                "verbose_name_plural": "Found Vulnerabilities",
                "ordering": ["-found_on"],
            },
        ),
    ]
