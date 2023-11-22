from django.shortcuts import render, redirect
from .models import UploadedFile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import pandas as pd
import os
from django.shortcuts import render, redirect
from django.conf import settings
from .models import UploadedFile

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
        valid_extensions = ['xlsx', 'json', 'csv', 'xls']
        if file_extension not in valid_extensions:
            error_message = "Invalid file format. Please upload a file with valid extension (xlsx, xls, json, or csv)."
        else:
            # Save using UploadedFile model
            uploaded_file_instance = UploadedFile(file=uploaded_file,)
            
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
        
    return render(request, 'import.html')

# Views for downloading sample files 
from django.http import FileResponse
def download_sample_excel(request):
    file_path = os.path.join('uploads', 'sample_files', 'sample_excel_format.xlsx')
    response = FileResponse(open(file_path, 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=sample_excel_format.xlsx'
    return response;

# TODO: Update
def download_sample_csv(request):
    file_path = os.path.join('uploads', 'sample_files', 'sample_excel.xlsx')
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename=sample_excel.xlsx'
    return response;

# TODO: Update
def download_sample_json(request):
    file_path = os.path.join('sample_files', 'sample_excel.xlsx')
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename=sample_excel.xlsx'
    return response

# %******************** Export File Page ****************************%

def ExportPage(request):
    return render(request, "export.html")


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
