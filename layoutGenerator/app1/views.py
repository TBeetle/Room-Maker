from django.shortcuts import render, redirect
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
            # Create new UploadedFile object and set the name
            uploaded_file_obj = UploadedFile(
                file=uploaded_file, file_name=uploaded_file.name
            )

            # Set the user attribute for the uploaded file if they are authenticated
            if request.user.is_authenticated:
                uploaded_file_obj.user = request.user

            # Save uploaded file
            uploaded_file_obj.save()

            # Get the file name
            file_name = uploaded_file_obj.file_name

            # Redirect to export page
            return redirect("export-page")
    
    else:
        error_message = None    # Initialize error_message variable

    # Define context with 'file_name' and 'error_message' to pass to HTML
    context = {
        'file_name': file_name,
        'error_message' : error_message
    }
    return render(request, "import.html", context)


def ExportPage(request):
    return render(request, "export.html")


def RegisterPage(request):
    return render(request, "register.html")


def LoginPage(request):
    return render(request, "login.html")


def HomePage(request):
    return render(request, "home.html")
