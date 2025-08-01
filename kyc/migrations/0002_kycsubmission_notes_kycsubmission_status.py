# Generated by Django 4.2 on 2025-07-03 16:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kyc", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="kycsubmission",
            name="notes",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="kycsubmission",
            name="status",
            field=models.CharField(
                choices=[
                    ("SUCCESS", "Success"),
                    ("FAILED", "Failed"),
                    ("PENDING", "Pending"),
                ],
                default="PENDING",
                max_length=10,
            ),
        ),
    ]
