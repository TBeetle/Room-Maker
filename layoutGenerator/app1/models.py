from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse # Generate URLs of individual objects through reversing URL patterns
# Create your models here.

# User model is predefined by Django, containing all necessary fields


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator

class UploadedFile(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)    # Identifier of user who uploaded file
    uploaded_at = models.DateTimeField(auto_now_add=True)   # Timestamp indicating when file was uploaded

    file = models.FileField(
        upload_to='imported_files/',
        default='placeholder.txt',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'json', 'csv', 'txt'])]
        );  # Store uplaaded file
    
    file_name = models.CharField(max_length=255) # Added to track name of file
    file_path = models.CharField(max_length=255, blank=True)    # Path to uploaded file on server
    file_type = models.CharField(max_length=10)     # Store file type (Excel, JSON, or CSV)
    
    def __str__(self):
        return self.file_name

# Stores generated LaTeX code and reference to original file 
class ConvertedFile(models.Model):
    # TODO: Update Github schema with file_name
    file_name = models.CharField(max_length=255)
    # TODO: Update 'userid' with 'user'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    # TODO: Add a field for LaTeX code; likely some kind of text document OR a LaTeX file?
    latex_code = models.TextField()
    created_at = models.DateTimeField

    def __str__(self):
        return self.file_name
    
# Represents a user-defined layout, storing various style settings
class Layout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    # TODO: Eventually update these to store pre-defined color/font settings instead of charfields ??
    
    font_type = models.CharField(max_length=255)
    font_size = models.IntegerField()
    font_color = models.CharField(max_length=7) # Use a hex color code
    
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
    default_boundary_colors = models.TextField()    # Use a hex color code
    created_at = models.DateTimeField(auto_now_add=True)
