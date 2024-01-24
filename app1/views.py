from django.shortcuts import render, redirect
from .models import UploadedFile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages, admin
from django.core.files.base import ContentFile
from django.utils.text import slugify, get_valid_filename

import pandas as pd
import os
from django.shortcuts import render, redirect
from django.conf import settings
from .models import UploadedFile, ConvertedFile
from django.shortcuts import HttpResponse
import zipfile
import app1.latex_conversion as lc

# Modules for handling file validation:
from django.http import HttpResponseBadRequest



# %******************** Import File Page ****************************%

# Home page view of the website, where users can upload a file
@login_required(login_url="login")
def ImportPage(request):

    # Ensure request is a POST and that a file was uploaded:
    if request.method == "POST" and request.FILES:
        uploaded_file = request.FILES["uploaded_file"]
        username = request.user.username

        # File extension validation:
        file_extension = uploaded_file.name.split('.')[-1]  # Get file extension
        valid_extensions = ['xlsx', 'json', 'csv']
        if file_extension not in valid_extensions:
            messages.info(request, "Invalid file format. Please upload a file with valid extension (xlsx, json, or csv).")
        else:

            # Rename file to have no spaces
            uploaded_file.name = get_valid_filename(uploaded_file.name)
            print("File name: " + uploaded_file.name)

            # Create an UploadedFile instance with base file
            uploaded_file_instance = UploadedFile(
                file=uploaded_file,
                user=request.user,
                )

            # Define path to uploaded JSON/CSV file - /uploads/imported_files/<filename>
            uploaded_filename = uploaded_file_instance.file.name
            print("uploaded_filename: " + uploaded_filename)
            uploaded_file_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, uploaded_filename)
            print("Uploaded CSV/JSON File Path: " + uploaded_file_path)
            print("Uploaded file name: " + uploaded_filename)

            # Save UploadedFile instance to server
            uploaded_file_instance.file_name = uploaded_filename
            uploaded_file_instance.save()

            print("CHECK 1 COMPLETE: File Uploaded to /imported_files")

            # Convert file from CSV/JSON to Excel
            if file_extension != 'xlsx':
                if file_extension == "csv":
                    # Read CSV into a dataframe
                    df = pd.read_csv(uploaded_file_path)

                if file_extension == "json":
                    # Read JSON into a dataframe
                    df = pd.read_json(uploaded_file_path)

                # Rename file
                prefix_filename, _ = os.path.splitext(uploaded_filename)
                converted_filename = f"{prefix_filename}.xlsx"

                # Create new Excel workbook at /uploads/imported_files/<filename>.xlsx
                excel_filepath = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, converted_filename)
                df.to_excel(excel_filepath, index=False)

                # Update UploadedFile with new converted Excel File
                with open(excel_filepath, 'rb') as excel_file:
                    # Create ContentFile to hold contents of Excel file
                    excel_content = ContentFile(excel_file.read())
                    
                    # Update UploadedFile instance with:
                    uploaded_file_instance.file_name = converted_filename   # Add .xlsx
                    uploaded_file_instance.file = excel_content # Update file with Excel file contens
                    uploaded_file_instance.file_path = excel_filepath   # Add filepath: uploads/imported_files/<file>.xlsx

                # Updated path to Excel file
                uploaded_file_path = excel_filepath
                print("Uploaded File Path: " + uploaded_file_path)
                uploaded_file_instance.save()
            else:
                uploaded_file_instance.file_path = uploaded_file_path
                uploaded_file_instance.save()
            
            # Error checking:
            print("*** File name: " + uploaded_file_instance.file_name)
            print("*** File path: " + uploaded_file_instance.file_path)

            # Call conversion code on file from /uploads/imported_files/<filename>
            lc.conversion(uploaded_file_path)

            # After conversion, create a ConvertedFile instance and store the produced LaTeX code & PDF

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

    

# %******************** Export File Page ****************************%

def download_pdf(request):
    file_path = os.path.join('uploads', 'conversion_output', 'output.pdf')  # Make sure the file exists and this path is correct
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=output.pdf'
            return response
    else:
        return HttpResponse("File not found", status=404)

def download_tex(request):
    file_path = os.path.join('uploads', 'conversion_output', 'output.tex')  # Update this path to your .tex file
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/x-tex')
            response['Content-Disposition'] = 'attachment; filename=output.tex'
            return response
    else:
        return HttpResponse("File not found", status=404)

def download_zip(request):
    pdf_path = os.path.join('uploads', 'conversion_output', 'output.pdf')  # Path to your PDF file
    tex_path = os.path.join('uploads', 'conversion_output', 'output.tex')  # Path to your Tex file

    # Check if both files exist
    if os.path.exists(pdf_path) and os.path.exists(tex_path):
        # Create a zip file
        zip_file_path = os.path.join('uploads', 'conversion_output', 'output.zip')
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

@login_required(login_url="login")
def StyleSettingsPage(request):
    # Retrieve user-specific default layout settings
    default_style_settings = DefaultStyleSettings.objects.get_or_create(user=request.user)

    #TODO: Handle form submission for user to update their default layout settings
    # if request.method == 'POST':
        # form = DefaultStyleSettingsForm(request.POST, instance=default_style_settings)
        # if form.is_valid():
        #    form.save()
        #    return redirect('settings') # Redirect to settings page after editing

    return render(request, "style-settings.html")

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
