# Generated by Django 4.2.6 on 2023-11-09 22:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app1", "0003_alter_uploadedfile_file"),
    ]

    operations = [
        migrations.AlterField(
            model_name="uploadedfile",
            name="file",
            field=models.FileField(
                blank=True,
                default="placeholder.txt",
                null=True,
                upload_to="imported_files/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["xlsx", "json", "csv", "txt"]
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="uploadedfile",
            name="file_path",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
