from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import (
    reverse,
)  # Generate URLs of individual objects through reversing URL patterns

# Create your models here.

# User model is predefined by Django, containing all necessary fields


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator
from datetime import datetime


# Represents an uploaded file, storing a predefined file imported by the user to be converted into a LaTeX / PDF file
class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Identifier of user who uploaded file
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp indicating when file was uploaded

    # Original file uploaded by user
    file = models.FileField(
        upload_to="imported_files/",
        default="placeholder.txt",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["xlsx", "json", "csv", "xls"])
        ],
    )

    file_name = models.CharField(max_length=255, default="")

    file_path = models.CharField(
        max_length=255, blank=True
    )  # Path to uploaded file on server

    file_type = models.CharField(max_length=10)  # Store file type (Excel, JSON, or CSV)

    def save(self, *args, **kwargs):
        # Set default value for file_name to the uploaded file's name
        if not self.file_name:
            self.file_name = self.file.name.replace(" ", "_")

        super(UploadedFile, self).save(*args, **kwargs)

    def __str__(self):
        return self.file_name


# Stores generated LaTeX code and reference to original file
class ConvertedFile(models.Model):
    file_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # Links to associated UploadedFile
    original_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)

    # To hold LaTeX code
    latex_code = models.FileField(
        upload_to="latex_files/",
        default="default-layout.tex",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["tex"])],
    )

    # TODO: add file field for PDF associated with layout

    def __str__(self):
        return self.file_name


# Represents a user-defined layout, storing various style settings
class Layout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    # TODO: Eventually update these to store pre-defined color/font settings instead of charfields ??

    font_type = models.CharField(max_length=255)
    font_size = models.IntegerField()
    font_color = models.CharField(max_length=7)  # Use a hex color code

    boundary_colors = models.TextField()
    orientation_type = models.CharField(max_length=255)

    image_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


# Stores default style settings for users, providing defaults for new layouts and ensuring consistency
class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_font_type = models.CharField(max_length=255)
    default_font_size = models.IntegerField()
    default_font_color = models.CharField(max_length=7)
    default_boundary_colors = models.TextField()  # Use a hex color code
    created_at = models.DateTimeField(auto_now_add=True)
