from django.shortcuts import render, redirect, HttpResponse
from .models import UploadedFile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Modules for handling file validation:
from django.http import HttpResponseBadRequest


# Home page view of the website, where users can upload a file
@login_required(login_url="login")
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
