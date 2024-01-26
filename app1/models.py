from django.db import models
from django.contrib.auth.models import User
from layoutGenerator import settings
import os
from django.urls import (
    reverse,
)  # Generate URLs of individual objects through reversing URL patterns

# Create your models here.

# User model is predefined by Django, containing all necessary fields


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator
from datetime import datetime

def get_user_subfolder(instance, filename):
    # Returns the path to a user's specific subfolder in 'imported_files'
    return f'imported_files/{instance.user.username}/{filename}'

# Represents an uploaded file, storing a predefined file imported by the user to be converted into a LaTeX / PDF file
class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Identifier of user who uploaded file
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp indicating when file was uploaded

    # Original file uploaded by user
    file = models.FileField(
        upload_to=get_user_subfolder,
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

        # Create a subdirectory for user in 'imported_files' if it does not exist
        user_folder = os.path.join(settings.MEDIA_ROOT, 'imported_files', self.user.username)
        os.makedirs(user_folder, exist_ok=True)

        super(UploadedFile, self).save(*args, **kwargs)

    def __str__(self):
        return self.file_name


# Stores generated LaTeX code and reference to original file
class ConvertedFile(models.Model):
    
    file_name = models.CharField(max_length=255) # Stores the PREFIX (without extension)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=255, default="NONE")

    # Links to associated UploadedFile
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)

    # Reference to latex file in form 'uploads/imported_files/<username>/file_name.tex'
    latex_file = models.CharField(max_length=255,
                                  default= os.path.join(settings.MEDIA_ROOT,'conversion_output', 'output.tex'))

    # Reference to PDF file in form 'uploads/imported_files/<username>/file_name.pdf
    pdf_file = models.CharField(max_length=255,
                                default= os.path.join(settings.MEDIA_ROOT,'conversion_output', 'output.pdf'))

    def save(self, *args, **kwargs):
        # Set default value for file_name from uploaded_file
        if not self.file_name:
            self.file_name = self.uploaded_file.file_name

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
