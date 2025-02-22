# Generated by Django 5.0 on 2024-01-24 17:03

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app1", "0004_alter_uploadedfile_file_alter_uploadedfile_file_path"),
    ]

    operations = [
        migrations.AddField(
            model_name="convertedfile",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="convertedfile",
            name="latex_code",
            field=models.FileField(
                blank=True,
                default="default-layout.tex",
                null=True,
                upload_to="latex_files/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["tex"]
                    )
                ],
            ),
        ),
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
                        allowed_extensions=["xlsx", "json", "csv", "xls"]
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="uploadedfile",
            name="file_name",
            field=models.CharField(default="", max_length=255),
        ),
    ]
