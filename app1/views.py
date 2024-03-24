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
from .models import UploadedFile, ConvertedFile, StyleSettings, DefaultStyleSettings, Label
from django.shortcuts import HttpResponse
from django.http import HttpResponseNotFound
import zipfile
import app1.latex_conversion as lc
import six
from django.http import HttpResponseRedirect

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
from django.urls import reverse

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

                # File extension and file name validation:
                file_extension = uploaded_file.name.split('.')[-1]  # Get file extension
                valid_extensions = ['xlsx', 'json', 'csv']
                uploaded_files_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', username)
                file_path = os.path.join(uploaded_files_path, uploaded_file.name)
                if file_extension not in valid_extensions:
                    messages.info(request, "Invalid file format. Please upload a file with valid extension (xlsx, json, or csv).")
                elif os.path.exists(file_path):
                    messages.info(request, "File with the same name already exists. Please choose a different file name.")
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

                    # Query for DefaultStyleSettings based on user preferences
                    default_styling = DefaultStyleSettings.objects.filter(user=request.user).first()

                    print("font: " + default_styling.font_type)
                    # Create individual StyleSettings for layout
                    layout_style = StyleSettings(
                        user = request.user,
                        name = converted_filename,
                        wall_color = default_styling.wall_color,
                        door_color = default_styling.door_color,
                        furniture_color = default_styling.furniture_color,
                        window_color = default_styling.window_color,
                        navigation_arrow_color = default_styling.navigation_arrow_color,
                        sensor_label_color = default_styling.sensor_label_color,
                        camera_label_color = default_styling.camera_label_color,
                        calibration_color = default_styling.calibration_color,
                        wall_width = default_styling.wall_width,
                        door_width = default_styling.door_width,
                        furniture_width = default_styling.furniture_width,
                        window_width = default_styling.window_width,
                        orientation_type = "vertical"
                    )
                    layout_style.save()

                    

                    # Call conversion code on file from /uploads/imported_files/<filename>
                    success = lc.conversion(uploaded_file_path, layout_style)
                    if not success:
                        try:
                            # Delete uploaded file and associated instance
                            os.remove(uploaded_file_instance.file_path)
                            uploaded_file_instance.delete()
                        except Exception as e:
                            logger.error("Error occurred while deleting file: %s", e)
                            messages.error(request, "An error occurred while deleting the file.")
                        
    
                    
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

                    print("reached here")

                    # Create Label objects by parsing through Excel file
                    labels = parse_excel_file(converted_file)
                    for label in labels:
                        print("label: " + label['name'])
                        Label.objects.create(file=converted_file, name=label['name'], 
                                             x_coordinate=label['x_coordinate'], y_coordinate=label['y_coordinate'])

                    print("created labels")

                    return redirect("export-layout", layout_id=converted_file.id)
        except Exception as e:
            logger.error("Error occurred during import: %s", e)
            messages.error(request, "The uploaded file could not be parsed.")
            return redirect("import")

    return render(request, 'import.html')

# parse through Excel file to identify labels 
def parse_excel_file(converted_file):
    # read excel file into df
    df = pd.read_excel(converted_file.file_path)
    labels = []

    # iterate over rows in dataframe to extract labels
    for index, row in df.iterrows():
        if row['Type'] in ['Camera', 'Sensor', 'Calibration', 'Room Navigation']:
            # extract data for the label
            label_data = {
                'name': row['Descriptor'],
                'x_coordinate': row['X'],
                'y_coordinate': row['Y']
            }

            labels.append(label_data)

    return labels

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

def download_pdf(request, layout_id):
    layout = get_object_or_404(ConvertedFile, id=layout_id)
    file_path = layout.pdf_file
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    else:
        return HttpResponse("File not found", status=404)

def download_tex(request, layout_id):
    layout = get_object_or_404(ConvertedFile, id=layout_id)
    file_path = layout.latex_file
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/x-tex')
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    else:
        return HttpResponse("File not found", status=404)

def download_zip(request, layout_id):
    layout = get_object_or_404(ConvertedFile, id=layout_id)
    pdf_path = layout.pdf_file
    tex_path = layout.latex_file

    # Check if both files exist
    if os.path.exists(pdf_path) and os.path.exists(tex_path):
        # Create a zip file
        zip_file_path = os.path.join('uploads', 'conversion_output', f'{layout_id}.zip')
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            zipf.write(pdf_path, os.path.basename(pdf_path))
            zipf.write(tex_path, os.path.basename(tex_path))

        # Serve the zip file for download
        with open(zip_file_path, 'rb') as zip_file:
            zip_file_name = os.path.basename(pdf_path).replace('.pdf', '') + '.zip'
            response = HttpResponse(zip_file.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename={zip_file_name}'
            return response
    else:
        return HttpResponse("One or more files not found", status=404)

from .forms import UpdateFileNameForm

from shutil import move

@login_required(login_url="login")
def ExportPage(request, layout_id):
    # Retreive layout based on layout id
    layout = ConvertedFile.objects.get(id=layout_id)
    print("layout name: " + layout.file_name)
    print("pdf file: " + layout.pdf_file)

    if request.method == 'POST':
        update_file_name_form = UpdateFileNameForm(request.POST, instance=layout)
        if update_file_name_form.is_valid():
            new_file_name = update_file_name_form.cleaned_data['new_file_name']
            old_file_name = layout.file_name
            layout.file_name = new_file_name
            layout.save()

            # rename associated files in user's uploaded file directory
            user_directory = os.path.join(settings.MEDIA_ROOT, 'imported_files', request.user.username)
            for file_extension in ['.pdf', '.tex', '.png', '.xlsx']:
                old_file_path = os.path.join(user_directory, f"{old_file_name}{file_extension}")
                new_file_path = os.path.join(user_directory, f"{new_file_name}{file_extension}")
                if os.path.exists(old_file_path):
                    move(old_file_path, new_file_path)
            
            # update database for associated files

            print("File name updated successfully")
            return redirect('export-layout', layout.id)
    else:
        update_file_name_form = UpdateFileNameForm(instance=layout, initial={'new_file_name': layout.file_name})

    context = {
        'layout': layout,
        'update_file_name_form': update_file_name_form,
    }
    return render(request, 'export.html', context)

# Support view for serving images through Django instead of directly through file system
def serve_image(request, image_path):
    absolute_path = os.path.join(settings.MEDIA_ROOT, image_path)
    try:
        # Open the image file in binary
        with open(absolute_path, 'rb') as f:
            image_data = f.read()
        content_type = 'image/png' # Set content type as .png image for HTTP response
        # Create HTTP response with image data and content type
        return HttpResponse(image_data, content_type=content_type)
    except FileNotFoundError:
            # Handle the case where the file is not found
            return HttpResponseNotFound("Image not found")

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
            print(f"Nav color = {style_settings_instance.navigation_arrow_color}")
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
from .forms import UpdateStyleSettingsForm, LabelForm
from django.shortcuts import render, get_object_or_404, redirect
from django import forms


# Allows user to update the styling of a specific layout
@login_required(login_url="login")
def EditLayoutStylePage(request, layout_id):
    
    layout = get_object_or_404(ConvertedFile, id=layout_id)
    style_settings_instance = layout.style_settings
    labels = layout.get_labels()

    if request.method == "POST":
        # Style settings form
        form = UpdateStyleSettingsForm(request.POST, instance=style_settings_instance)

        # Process orientation field
        orientation = request.POST.get('orientation')
        style_settings_instance.orientation = orientation  # Update orientation value
        style_settings_instance.save()

        # Initialize list to hold label forms
        label_forms = [LabelForm(request.POST, prefix=str(label.id), initial={'x_coordinate': label.x_coordinate, 'y_coordinate': label.y_coordinate}) for label in labels]

        # Check if both forms are valid
        if form.is_valid() and all(label_form.is_valid() for label_form in label_forms):
            # Save style settings form
            form.save()
            print(f"Style settings form successfully saved.")
            
            # Process label forms
            for label, label_form in zip(labels, label_forms):
                # Update coordinates for the label
                label.x_coordinate = label_form.cleaned_data['x_coordinate']
                label.y_coordinate = label_form.cleaned_data['y_coordinate']
                label.save()
                print(f"Label {label.name} saved with new coordinates X: {label.x_coordinate}, Y: {label.y_coordinate}")
            return redirect('edit-layout', layout_id=layout_id)
        
        else:
            print("one or more forms are invalid.")
            # TODO: Handle form validation errors
    else:
        # Initialize style settings form
        form = UpdateStyleSettingsForm(instance=style_settings_instance)
        # Initialize orientation form
        orientation_initial = style_settings_instance.orientation  # Get initial orientation value
        orientation_form = forms.CharField(initial=orientation_initial, widget=forms.HiddenInput())  # Hidden input for storing orientation
        # Initialize label forms
        label_forms = [LabelForm(prefix=str(label.id), initial={'x_coordinate': label.x_coordinate, 'y_coordinate': label.y_coordinate}) for label in labels]

    context = {
        'layout': layout,
        'form': form,
        'labels': labels,
        'label_data': zip(labels, label_forms),
        'orientation_form': orientation_form,  # Pass orientation form to the template
    }

    return render(request, "edit-style.html", context)

# %******************** Layout Library Page ****************************%

from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import ConvertedFile
from django.db.models import F

@login_required(login_url="login")
def LayoutLibraryPage(request):
    filter_value = request.GET.get('filter')
    if filter_value == 'alphabetical':
        user_layouts = ConvertedFile.objects.filter(user=request.user).order_by('file_name')
    else:  # Default to 'last_modified'
        user_layouts = ConvertedFile.objects.filter(user=request.user).order_by('-last_modified')

    return render(request, 'layout-library.html', {'layouts': user_layouts, 'filter_value': filter_value})

    # paginator = Paginator(user_layouts, 9)  # Show 9 layouts per page

    # page_number = request.GET.get('page')
    # try:
    #     layouts = paginator.page(page_number)
    # except PageNotAnInteger:
    #     layouts = paginator.page(1)
    # except EmptyPage:
    #     layouts = paginator.page(paginator.num_pages)

    # return render(request, 'layout-library.html', {'layouts': layouts, 'filter_value': filter_value})


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

# %******************* Account Settings ****************************%

from django.contrib.auth import update_session_auth_hash
from .forms import AccountSettingsForm

@login_required(login_url="login")
def AccountSettingsPage(request):
    user = request.user
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            old_password = form.cleaned_data.get('old_password')
            new_password = form.cleaned_data.get('new_password1')
            if old_password and new_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password updated successfully.')
            messages.success(request, 'Account settings updated successfully.')
    else:
        form = AccountSettingsForm(instance=user)
    return render(request, 'account-settings.html', {'form': form})

# %******************** User Registration ****************************%
import re

def RegisterPage(request):
    if request.method=='POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        email = email.lower()
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        # Check if any field is empty
        if not uname or not email or not pass1 or not pass2:
            messages.error(request, 'All fields are required.')

        # Check if email or username is already in use
        elif User.objects.filter(username=uname).exists():
            messages.error(request, 'Username is already in use.')

        elif not re.fullmatch(regex, email):
            messages.error(request, 'Invalid email format.')

        elif User.objects.filter(email=email.lower()).exists():
            messages.error(request, 'Email is already in use.')
        
        elif pass1 != pass2:
            messages.info(request, "Passwords do not match!")

        else:
            # Create a new user
            my_user = User.objects.create_user(uname, email, pass1)
            my_user.save()
            # create new default style settings
            default_style_settings = DefaultStyleSettings(user=my_user)
            default_style_settings.save()

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

# def ForgotPassword(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         try:
#             user = User.objects.get(email=email)
#             # Generate a unique token for password reset (you can use Django's built-in token generator)
#             # Reset token generation code goes here...
#             # token = ...
#             token = token_generator.make_token(user)

#             # Send password reset email
#             subject = 'Password Reset Instructions'
#             html_message = render_to_string('password-reset-email.html', {'token': token})
#             plain_message = strip_tags(html_message)
#             from_email = 'backyardigansreset@gmail.com'  # Set your email address
#             to_email = user.email
#             send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
#             messages.success(request, 'Password reset instructions sent to your email.')
#             return redirect('login')  # Redirect to login page
#         except User.DoesNotExist:
#             messages.error(request, 'User with this email does not exist.')
#     return render(request, 'forgot-password.html')

from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ValidationError
#from django.utils.encoding import force_text

# from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# def ResetPassword(request, uidb64, token):
#     try:
#         uid = urlsafe_base64_decode(uidb64).decode()  # Decode the uidb64 to a string
#         user = User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
#         user = None

#     if user is not None and PasswordResetTokenGenerator().check_token(user, token):
#         # Process password reset form submission
#         if request.method == 'POST':
#             password = request.POST.get('password')
#             confirm_password = request.POST.get('confirm_password')
#             if password == confirm_password:
#                 user.set_password(password)
#                 user.save()
#                 messages.success(request, 'Password reset successfully.')
#                 return redirect('login')  # Redirect to login page
#             else:
#                 messages.error(request, 'Passwords do not match.')
#     else:
#         messages.error(request, 'Invalid link for password reset.')
#         return redirect('login')  # Redirect to login page

#     return render(request, 'password-reset.html', {'uidb64': uidb64, 'token': token})

from django.core.files.storage import default_storage

# %******************** Delete button ****************************%
@login_required(login_url="login")
def delete_layout_test(request, layout_id):
    try:
        layout = ConvertedFile.objects.get(id=layout_id, user=request.user)  # Ensure the user can only delete their own layouts
        # delete associated files
        default_storage.delete(layout.file_path)
        default_storage.delete(layout.latex_file)
        default_storage.delete(layout.pdf_file)
        default_storage.delete(layout.image)
        # delete layout instance
        layout.delete()
        print("Layout deleted.")
    except ConvertedFile.DoesNotExist:
        messages.error(request, "Layout not found.")
    except Exception as e:
        messages.error(request, "Error deleting layout: %s" % e)
    return HttpResponseRedirect(reverse('layout-library'))