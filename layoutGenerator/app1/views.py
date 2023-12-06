from django.shortcuts import render, redirect
from .models import UploadedFile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.base import ContentFile

import pandas as pd
import os
from django.shortcuts import render, redirect
from django.conf import settings
from .models import UploadedFile
from django.shortcuts import HttpResponse
import zipfile
import app1.latex_conversion as lc

# Modules for handling file validation:
from django.http import HttpResponseBadRequest


# %******************** Import File Page ****************************%

# Home page view of the website, where users can upload a file
@login_required(login_url="login")
def ImportPage(request):

    file_name = None # Initialize the file name variable
    error_message = None

    # Ensure request is a POST and that a file was uploaded:
    if request.method == "POST" and request.FILES:
        uploaded_file = request.FILES["uploaded_file"]

        # File extension validation:
        file_extension = uploaded_file.name.split('.')[-1]  # Get file extension
        valid_extensions = ['xlsx', 'json', 'csv']
        if file_extension not in valid_extensions:
            error_message = "Invalid file format. Please upload a file with valid extension (xlsx, json, or csv)."
        else:

            # If CSV: Convert CSV file into Excel to prepare for conversion
            if file_extension == "csv":
                # Create an UploadedFile instance for the original uploaded file
                uploaded_file_instance = UploadedFile(file=uploaded_file,)

                if request.user.is_authenticated:
                    uploaded_file_instance.user = request.user
                uploaded_file_instance.save()

                # Determine the path of the saved file
                saved_file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file_instance.file.name)

                # Read CSV into a DataFrame
                df = pd.read_csv(saved_file_path)

                # Rename the file to an Excel file
                prefix_file_name, _ = os.path.splitext(uploaded_file_instance.file_name)    # Split file name frmo extension
                converted_file_name = f"{prefix_file_name}.xlsx"

                # Create a new Excel workbook
                excel_file_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', converted_file_name)
                df.to_excel(excel_file_path, index=False)

                # Save the converted Excel file as a new UploadedFile instance
                with open(excel_file_path, 'rb') as excel_file:
                    # Create ContentFile to represent contents of Excel File
                    excel_content = ContentFile(excel_file.read())
                    # Create UploadedFile instance with the uploaded Excel file
                    converted_file_instance = UploadedFile(
                        file_name= converted_file_name,
                        file=excel_content,
                    )
                    # Save file path
                    converted_file_instance.file_path = excel_file_path
                    if request.user.is_authenticated:
                        converted_file_instance.user = request.user
                    converted_file_instance.save()

                # Set file_name to correct name for display or further use
                file_name = converted_file_instance.file_name

                # Call conversion code
                lc.conversion(excel_file_path)   

            # If Excel: Convert as normal
            if file_extension == 'xlsx':
                # Save using UploadedFile model
                uploaded_file_instance = UploadedFile(file=uploaded_file,)
                
                if request.user.is_authenticated:
                    uploaded_file_instance.user = request.user
                uploaded_file_instance.save()
                
                # Determine the path of the saved file
                saved_file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file_instance.file.name)

                # Call conversion code
                lc.conversion(saved_file_path)
          
            # Redirect to export page
            return redirect("export")
        
    return render(request, 'import.html')

#  Download sample Excel file for formmating
from django.http import FileResponse
def download_sample_excel(request):
    file_path = os.path.join('uploads', 'sample_files', 'example_excel_format.xlsx')
    response = FileResponse(open(file_path, 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=example_excel_format.xlsx'
    return response

# Download sample CSV file for formmating
def download_sample_csv(request):
    file_path = os.path.join('uploads', 'sample_files', 'example_csv_format.csv')
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename=example_csv_format.csv'
    return response

#  Download sample JSON file for formmating
def download_sample_json(request):
    file_path = os.path.join('uploads', 'sample_files', 'example_json_format.json')
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename=example_json_format.json'
    return response

def download_pdf(request):
    file_path = os.path.join('uploads', 'imported_files', 'output.pdf')  # Make sure the file exists and this path is correct
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=output.pdf'
            return response
    else:
        return HttpResponse("File not found", status=404)
    
def download_tex(request):
    file_path = os.path.join('uploads', 'imported_files', 'output.tex')  # Update this path to your .tex file
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/x-tex')
            response['Content-Disposition'] = 'attachment; filename=output.tex'
            return response
    else:
        return HttpResponse("File not found", status=404)

def download_zip(request):
    pdf_path = os.path.join('uploads', 'imported_files', 'output.pdf')  # Path to your PDF file
    tex_path = os.path.join('uploads', 'imported_files', 'output.tex')  # Path to your Tex file

    # Check if both files exist
    if os.path.exists(pdf_path) and os.path.exists(tex_path):
        # Create a zip file
        zip_file_path = os.path.join('uploads', 'imported_files', 'output.zip')
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            zipf.write(pdf_path, os.path.basename(pdf_path))
            zipf.write(tex_path, os.path.basename(tex_path))

        # Serve the zip file for download
        with open(zip_file_path, 'rb') as zip_file:
            response = HttpResponse(zip_file.read(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=output.zip'
            return response
    else:
        return HttpResponse("One or more files not found", status=404)

# %******************** Export File Page ****************************%

@login_required(login_url="login")
def ExportPage(request):
    return render(request, "export.html")

# %******************** Layout Library Page ****************************%

@login_required(login_url="login")
def LayoutLibraryPage(request):
    return render(request, "layout-library.html")


# %******************** Settings Pages ****************************%

@login_required(login_url="login")
def SettingsPage(request):
    return render(request, "settings.html")

# %******************** User Registration ****************************%

def RegisterPage(request):
    if request.method=='POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        if pass1 != pass2:
            messages.info(request, "Passwords do not match!")
            # return HttpResponse("Passwords do not match!")
        else:
            my_user = User.objects.create_user(uname, email, pass1)
            my_user.save()
            return redirect('login')
        # print(uname, email, pass1, pass2)

    return render(request, "register.html")

# %******************** Authentication pages ****************************%

def LoginPage(request):
    if request.method=="POST":
        username = request.POST.get("username")
        password = request.POST.get('pass')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('import')
        else:
            messages.info(request, "Username or password is incorrect!")
            #return HttpResponse("Username or password is incorrect!")
    return render(request, "login.html")

def LogoutPage(request):
    logout(request)
    # return redirect('login')
    return render(request, 'logout.html')

def HomePage(request):
    return render(request, "home.html")
