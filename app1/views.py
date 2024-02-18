from django.shortcuts import render, redirect
from .models import UploadedFile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages, admin
from django.core.files.base import ContentFile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.text import get_valid_filename
from shutil import copyfile
from django.conf import settings

import pandas as pd
import os
from django.shortcuts import render, redirect
from django.conf import settings
from .models import UploadedFile, ConvertedFile, StyleSettings, DefaultStyleSettings
from django.shortcuts import HttpResponse
import zipfile
import app1.latex_conversion as lc
import six

# Modules for handling file validation:
from django.http import HttpResponseBadRequest

# Sending email for password reset
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.db import transaction
import logging
logger = logging.getLogger(__name__)

from django.contrib.auth.tokens import PasswordResetTokenGenerator

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)
        )

token_generator = TokenGenerator()

# %******************** Import File Page ****************************%

# Home page view of the website, where users can upload a file
@login_required(login_url="login")
def ImportPage(request):

    # Ensure request is a POST and that a file was uploaded:
    if request.method == "POST" and request.FILES:
        # Ensure atomicity
        try:
            with transaction.atomic():
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

                    # Rename file
                    prefix_filename, _ = os.path.splitext(uploaded_filename)
                    converted_filename = f"{prefix_filename}.xlsx"

                    # Convert file from CSV/JSON to Excel
                    if file_extension != 'xlsx':
                        if file_extension == "csv":
                            # Read CSV into a dataframe
                            df = pd.read_csv(uploaded_file_path)

                        if file_extension == "json":
                            # Read JSON into a dataframe
                            df = pd.read_json(uploaded_file_path)

                        # Create new Excel workbook at /uploads/imported_files/<filename>.xlsx, relative to MEDIA_ROOT
                        excel_filepath = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, converted_filename)
                        print("Path to new Excel workbook:" + excel_filepath)
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

                    admin_user = User.objects.get(username='admin')
                    # Query for DefaultStyleSettings where the user is admin -- TODO, update to logged in user
                    default_styling = DefaultStyleSettings.objects.filter(user=admin_user).first()

                    # Create individual StyleSettings for layout
                    layout_style = StyleSettings(
                        user = request.user,
                        name = converted_filename,
                        text_decoration = default_styling.text_decoration,
                        font_type = default_styling.font_type,
                        font_color = default_styling.font_color,
                        font_size = default_styling.font_size,
                        wall_color = default_styling.wall_color,
                        door_color = default_styling.door_color,
                        furniture_color = default_styling.furniture_color,
                        window_color = default_styling.window_color,
                        wall_width = default_styling.wall_width,
                        door_width = default_styling.door_width,
                        furniture_width = default_styling.furniture_width,
                        window_width = default_styling.window_width,
                        orientation_type = "vertical"
                    )
                    layout_style.save()

                    print("User's default style settings: " + layout_style.font_color +" size: " + layout_style.font_type)

                    # Call conversion code on file from /uploads/imported_files/<filename>
                    lc.conversion(uploaded_file_path, layout_style)
                    print("Tyler Test")
                    
                    # Place .pdf, .png, and .tex files into user's subfolder at /uploads/imported_files/<username>/
                    prefix_filename, _ = os.path.splitext(uploaded_file_instance.file_name)
                    
                    source_tex_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.tex')
                    source_pdf_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.pdf')
                    source_png_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.png')
                    destination_tex_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, f"{prefix_filename}.tex")
                    destination_pdf_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, f"{prefix_filename}.pdf")
                    destination_png_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, f"{prefix_filename}.png")

                    copyfile(source_tex_path, destination_tex_path)
                    copyfile(source_pdf_path, destination_pdf_path)
                    copyfile(source_png_path, destination_png_path)
                    
                    # Make ConvertedFile to link UploadedFile with output
                    converted_file = ConvertedFile(
                        file_name=prefix_filename, # *NOTE* stores prefix without extension
                        user = request.user,
                        file_path = uploaded_file_instance.file_path,
                        uploaded_file = uploaded_file_instance,
                        latex_file = destination_tex_path,
                        pdf_file = destination_pdf_path,
                        style_settings = layout_style,
                        image = destination_png_path,
                    )
                    converted_file.full_clean()
                    converted_file.save(force_insert=True)

                    # Error checking - ensures that convertedfile exists
                    print(f"Converted file prefix: {converted_file.file_name}")
                    print(f"Converted file file_path: {converted_file.file_path}")

                    return redirect("export-layout", layout_id=converted_file.id)
        except Exception as e:
            logger.error("Error occurred during import: %s", e)
            messages.error(request, "An error occurred during import.")
            return redirect("import")

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
def ExportPage(request, layout_id):
    # Retreive layout based on layout id
    layout = ConvertedFile.objects.get(id=layout_id)
    context = {
        'layout': layout,
    }
    return render(request, "export.html", context)

# Support view for serving images through Django instead of directly through file system
def serve_image(request, image_path):
    absolute_path = os.path.join(settings.MEDIA_ROOT, image_path)
    # Open the image file in binary
    with open(absolute_path, 'rb') as f:
        image_data = f.read()
    content_type = 'image/png' # Set content type as .png image for HTTP response
    # Create HTTP response with image data and content type
    return HttpResponse(image_data, content_type=content_type)

# %******************** Edit Styling of Layout Page ****************************%

from .forms import UpdateStyleSettingsForm
from django.shortcuts import render, get_object_or_404, redirect

@login_required(login_url="login")
def EditLayoutStylePage(request, layout_id):
    
    layout = get_object_or_404(ConvertedFile, id=layout_id)
    style_settings_instance = layout.style_settings 

    # TODO - Ensure that saving the form will update the associated style_settings model
    if request.method == "POST":
        form = UpdateStyleSettingsForm(request.POST, instance=style_settings_instance)
        if form.is_valid():
            form.save()
            print(f"FORM STYLE SETTINGS CHECK: Wall Thickness = {style_settings_instance.wall_width}")
            print(f"Wall Color = {style_settings_instance.wall_color}")
            print("Form successfully saved.")
            # TODO: Display success message
            # TODO @ Tyler: Call the LaTeX code with the new model values & update the PDF *****
            return redirect('edit-layout', layout_id=layout_id)
    else:
        form = UpdateStyleSettingsForm(instance=style_settings_instance)

    context = {
        'layout': layout,
        'form': form
    }
    return render(request, "edit-style.html", context)
from .forms import UpdateStyleSettingsForm
from django.shortcuts import render, get_object_or_404, redirect


# Allows user to update the styling of a specific layout
@login_required(login_url="login")
def EditLayoutStylePage(request, layout_id):
    
    layout = get_object_or_404(ConvertedFile, id=layout_id)
    style_settings_instance = layout.style_settings 

    if request.method == "POST":
        form = UpdateStyleSettingsForm(request.POST, instance=style_settings_instance)
        if form.is_valid():
            form.save()
            print(f"FORM STYLE SETTINGS CHECK: Wall Thickness = {style_settings_instance.wall_width}")
            print(f"Wall Color = {style_settings_instance.wall_color}")
            print("Form successfully saved.")
            # TODO: Display success message
            # TODO @ Tyler: Call the LaTeX code with the new model values & update the PDF
            return redirect('edit-layout', layout_id=layout_id)
    else:
        form = UpdateStyleSettingsForm(instance=style_settings_instance)

    context = {
        'layout': layout,
        'form': form
    }
    return render(request, "edit-style.html", context)

# %******************** Layout Library Page ****************************%

@login_required(login_url="login")
def LayoutLibraryPage(request):

    # Get user's created layouts
    user_layouts = ConvertedFile.objects.filter(user=request.user).order_by('-created_at')

    # Paginate by a maximum of 9 layouts at a time
    paginator = Paginator(user_layouts, 9) 

    page_number = request.GET.get('page')
    try:
        user_layouts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        user_layouts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        user_layouts = paginator.page(paginator.num_pages)

    context = {
        'layouts': user_layouts,
    }

    return render(request, "layout-library.html", context)


# %******************** Settings Pages ****************************%

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect
from .forms import AccountSettingsForm, UpdateDefaultStyleSettingsForm

# Settings page allowing user to update their Default Style Settings
@login_required(login_url="login")
def SettingsPage(request):

    # Get user-specific DefaultStyleSettings
    style_settings_instance = get_object_or_404(DefaultStyleSettings, user=request.user)

    if request.method == 'POST':
        form = UpdateDefaultStyleSettingsForm(request.POST, instance=style_settings_instance)
        if form.is_valid(): 
            form.save()
            messages.success(request, "Style settings have been updated.")
            return render(request, "default-style-settings.html", {'form': form})
        else:
            messages.error(request, "Style settings have not been applied.")

    else:
        # Pre-populate the form with user's current style settings
        form = UpdateDefaultStyleSettingsForm(instance=style_settings_instance)

    return render(request, "default-style-settings.html", {'form' : form})

@login_required(login_url="login")
def AccountSettingsPage(request):

    if request.method == 'POST':
        # TODO: Update form so that when a user changes their email and returns to Account Settings, it correctly previews the updated email.
        form = AccountSettingsForm(request.user, request.POST, initial={'email': request.user.email})
        if form.is_valid():
            form.save()
            messages.success(request, "Changes have been saved.")
            updated_email = form.cleaned_data.get('email')
            return render(request, "account-settings.html", {'form': form, 'updated_email': updated_email})
        else:
            print(form.errors)
            messages.error(request, 'Changes not saved.')
    else:
        # pre-populate the form with the currently logged-in user's email address upon GET request
        form = AccountSettingsForm(request.user, initial={'email': request.user.email})

    return render(request, "account-settings.html", {'form': form})

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

def ForgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate a unique token for password reset (you can use Django's built-in token generator)
            # Reset token generation code goes here...
            # token = ...
            token = token_generator.make_token(user)

            # Send password reset email
            subject = 'Password Reset Instructions'
            html_message = render_to_string('password-reset-email.html', {'token': token})
            plain_message = strip_tags(html_message)
            from_email = 'backyardigansreset@gmail.com'  # Set your email address
            to_email = user.email
            send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
            messages.success(request, 'Password reset instructions sent to your email.')
            return redirect('login')  # Redirect to login page
        except User.DoesNotExist:
            messages.error(request, 'User with this email does not exist.')
    return render(request, 'forgot-password.html')

from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ValidationError
#from django.utils.encoding import force_text

# from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

def ResetPassword(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()  # Decode the uidb64 to a string
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
        user = None

    if user is not None and PasswordResetTokenGenerator().check_token(user, token):
        # Process password reset form submission
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, 'Password reset successfully.')
                return redirect('login')  # Redirect to login page
            else:
                messages.error(request, 'Passwords do not match.')
    else:
        messages.error(request, 'Invalid link for password reset.')
        return redirect('login')  # Redirect to login page

    return render(request, 'password-reset.html', {'uidb64': uidb64, 'token': token})



