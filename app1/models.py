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


# Represents the settings for styling associated with an individual layout
class StyleSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    # Allowed text decoration
    NO_DECORATION = 'none'
    BOLD = 'bold'
    UNDERLINE = 'underline'
    ITALICS = 'italics'

    TEXT_DECORATION_CHOICES = [
        (NO_DECORATION, 'None'),
        (BOLD, 'Bold'),
        (UNDERLINE, 'Underline'),
        (ITALICS, 'Italicize'),
    ]

    # Allowed fonts
    DEFAULT = 'Default'
    TIMES_NEW_ROMAN = 'Times New Roman'
    ARIAL = 'Arial'

    FONT_CHOICES = [
        (DEFAULT, 'Default'),
        (TIMES_NEW_ROMAN, 'Times New Roman'),
        (ARIAL, 'Arial'),
    ]

    # Text labels
    text_decoration = models.CharField(max_length=28, default=NO_DECORATION, choices=TEXT_DECORATION_CHOICES)  # Allowed values: bold, italicized, underlined
    font_type = models.CharField(max_length=56, default=DEFAULT, choices=FONT_CHOICES) # Font type
    font_size = models.IntegerField() # TODO: Set default
    font_color = models.CharField(max_length=7, default="#FFFFFF")

    # Colors using hex <#FFFFFF>
    wall_color = models.CharField(max_length=7, default="#FFFFFF")
    door_color = models.CharField(max_length=7, default="#FFFFFF")
    furniture_color = models.CharField(max_length=7, default="#FFFFFF")
    window_color = models.CharField(max_length=7, default="#FFFFFF")

    # Boundary widths
    wall_width = models.IntegerField()
    door_width = models.IntegerField()
    furniture_width = models.IntegerField()
    window_width = models.IntegerField()

    # TODO: Add Metadata styling

    # Orientation of PDF - horizontal or vertical
    orientation_type = models.CharField(max_length=255, default = "vertical")

    created_at = models.DateTimeField(auto_now_add=True)



# Stores default style settings for users, providing defaults for each layout they generate
class DefaultStyleSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Allowed text decoration
    NO_DECORATION = 'none'
    BOLD = 'bold'
    UNDERLINE = 'underline'
    ITALICS = 'italics'

    TEXT_DECORATION_CHOICES = [
        (NO_DECORATION, 'None'),
        (BOLD, 'Bold'),
        (UNDERLINE, 'Underline'),
        (ITALICS, 'Italicize'),
    ]

    # Allowed fonts
    DEFAULT = 'Default'
    TIMES_NEW_ROMAN = 'Times New Roman'
    ARIAL = 'Arial'

    FONT_CHOICES = [
        (DEFAULT, 'Default'),
        (TIMES_NEW_ROMAN, 'Times New Roman'),
        (ARIAL, 'Arial'),
    ]

    # Text labels
    text_decoration = models.CharField(max_length=28, default=NO_DECORATION, choices=TEXT_DECORATION_CHOICES)  # Allowed values: bold, italicized, underlined
    font_type = models.CharField(max_length=56, default=DEFAULT, choices=FONT_CHOICES) # Font type
    font_size = models.IntegerField(default=2) # TODO: Set defaults
    font_color = models.CharField(max_length=7, default="#FFFFFF")

    # Colors using hex <#FFFFFF>
    wall_color = models.CharField(max_length=7, default="#FFFFFF")
    door_color = models.CharField(max_length=7, default="#FFFFFF")
    furniture_color = models.CharField(max_length=7, default="#FFFFFF")
    window_color = models.CharField(max_length=7, default="#FFFFFF")

    # Boundary widths
    wall_width = models.IntegerField(default=2)
    door_width = models.IntegerField(default=2)
    furniture_width = models.IntegerField(default=2)
    window_width = models.IntegerField(default=2)

    created_at = models.DateTimeField(auto_now_add=True)

# Stores generated LaTeX code and reference to original file
class ConvertedFile(models.Model):
    file_name = models.CharField(max_length=255, default="name") # Stores the PREFIX (without extension)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)   # Automatically updated to current date and time when saved
    file_path = models.CharField(max_length=255, default="NONE")

    # link to associated StyleSettings
    style_settings = models.ForeignKey(StyleSettings, on_delete=models.CASCADE,
                                       null=True)

    # Link to associated UploadedFile
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)

    # Reference to latex file in form 'uploads/imported_files/<username>/file_name.tex'
    latex_file = models.CharField(max_length=255,
                                  default= os.path.join(settings.MEDIA_ROOT,'conversion_output', 'output.tex'))

    # Reference to PDF file in form 'uploads/imported_files/<username>/file_name.pdf
    pdf_file = models.CharField(max_length=255,
                                default= os.path.join(settings.MEDIA_ROOT,'conversion_output', 'output.pdf'))
    
    # Reference to PNG in form 'uploads/imported_files/<username>/file_name.png
    image = models.CharField(max_length=255,
                             default = os.path.join(settings.MEDIA_ROOT,'conversion_output', 'output.png'))

    def save(self, *args, **kwargs):
        # Set default value for file_name from uploaded_file
        if not self.file_name:
            self.file_name = self.uploaded_file.file_name

        # update paths for latex_file and pdf_file if the file_name is changed
        old_prefix = os.path.splitext(os.path.basename(self.latex_file))[0]
        new_prefix = os.path.splitext(self.file_name)[0]
        self.latex_file = self.latex_file.replace(old_prefix, new_prefix)
        self.pdf_file = self.pdf_file.replace(old_prefix, new_prefix)
        self.image = self.image.replace(old_prefix, new_prefix)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.file_name
    
    def convert_to_latex(self):
        try:
            # Retrieve the user's default style settings
            default_style_settings = DefaultStyleSettings.objects.get(user=self.user)
            
            # Call the conversion function with the default style settings
            latex_code = conversion(self.file, default_style_settings)
            
            # Return or save the LaTeX code as needed
        except DefaultStyleSettings.DoesNotExist:
            # Handle case where default style settings are not found
            print("Default style settings not found for the user.")