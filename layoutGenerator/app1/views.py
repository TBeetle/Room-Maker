import pandas as pd
import io
import os
import csv
from django.shortcuts import render, redirect
from django.conf import settings
from .models import UploadedFile

# Modules for handling file validation:
from django.http import HttpResponseBadRequest


# Home page view of the website, where users can upload a file
def ImportPage(request):

    file_name = None # Initialize the file name variable

    # Ensure request is a POST and that a file was uploaded:
    if request.method == "POST" and request.FILES:
        uploaded_file = request.FILES["uploaded_file"]

        # File extension validation:
        file_extension = uploaded_file.name.split('.')[-1]  # Get file extension
        valid_extensions = ['xlsx', 'json', 'csv']
        if file_extension not in valid_extensions:
            error_message = "Invalid file format. Please upload a file with valid extension (xlsx, json, or csv)."
        else:
            # Save using UploadedFile model
            uploaded_file_instance = UploadedFile(file=uploaded_file)
            
            if request.user.is_authenticated:
                uploaded_file_instance.user = request.user
            uploaded_file_instance.save()
            
            # Determine the path of the saved file
            saved_file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file_instance.file.name)

            if file_extension == 'xlsx':
                # Convert Excel to CSV
                df = pd.read_excel(saved_file_path)
                csv_file_name = uploaded_file.name.replace('.xlsx', '.csv')
                csv_file_path = os.path.join(settings.MEDIA_ROOT, csv_file_name)
                df.to_csv(csv_file_path, index=False)

                # Save the converted CSV file as a new UploadedFile instance
                with open(csv_file_path, 'rb') as csv_file:
                    converted_file_instance = UploadedFile(file_name=csv_file_name, file=csv_file)
                    
                    if request.user.is_authenticated:
                        converted_file_instance.user = request.user
                    converted_file_instance.save()

                file_name = converted_file_instance.file_name
            else:
                file_name = uploaded_file_instance.file_name

            # Redirect to export page
            return redirect("export-page")

    return render(request, "import.html", {'file_name': file_name, 'error_message': error_message})

def ExportPage(request):
    return render(request, "export.html")


def RegisterPage(request):
    return render(request, "register.html")


def LoginPage(request):
    return render(request, "login.html")


def HomePage(request):
    return render(request, "home.html")
