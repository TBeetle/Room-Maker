from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import StyleSettings, DefaultStyleSettings, ConvertedFile, Label

from django import forms
from django.forms import ModelForm

# forms.py
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User


class AccountSettingsForm(forms.ModelForm):
    """
    Form class for updating a user's account settings, including email and password changes.
    
    This form provides fields for updating the email address and/or password associated with a user's account,
    requiring the user to enter their current password twice in order to permit any changes.

    Fields:
        old_password: Field for user to enter their current (old) password
        new_password1: Field for user to enter their new password
        new_password2: Field for user to verify their new password
        email: Field for user to update email address

    Methods:
        clean(): Validation method for ensuring password criteria and verifying the user's current password

    """

    old_password = forms.CharField(label="Old Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    new_password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    # Ensure new passwords match given criteria & verify user's current password to allow changes
    def clean(self):
        # call parent cleaning methods
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        # Check if user entered values within new password fields
        if new_password1 or new_password2:
            # Perform data validation on new passwords
            if len(new_password1) < 8:
                self.add_error('new_password1', 'Password must contain at least 8 characters.')
            elif new_password1.isdigit():
                self.add_error('new_password1', 'Password cannot be entirely numeric.')
            if new_password1 != new_password2:
                self.add_error('new_password2', 'The two password fields didn’t match.')
            if not old_password:
                self.add_error('old_password', 'Please enter your old password.')
            else:
                user = self.instance
                if not user.check_password(old_password):
                    self.add_error('old_password', 'The old password is incorrect.')
                elif new_password1 == old_password:
                    self.add_error('new_password1', 'The new password is the same as the old password.')
        
        return cleaned_data


class UpdateFileNameForm(ModelForm):
    """
    Form class for updating the file name of the uploaded file associated with an imported layout.

    Fields:
        new_file_name: Field for user to enter new file name

    Methods:
        clean_new_file_name(): Cleans the given file name to follow standard file naming conventions, removing leading/trailing whitespace and
        replacing spaces in the string with underscores. Performs validation to prevent duplicate file names in user's library.
    """
    new_file_name = forms.CharField(label='New file name', widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=48, required=False)

    class Meta:
        model = ConvertedFile
        fields = ['new_file_name']

    def clean_new_file_name(self):
        new_file_name = self.cleaned_data['new_file_name'].strip()  # Remove leading and trailing whitespace

        # Check if the file name is blank after stripping whitespace
        if new_file_name == "":
            print("BLANK NAME")
            raise forms.ValidationError("File name cannot be blank.")
        
        # Replace space between characters with underscores
        new_file_name = new_file_name.replace(' ', '_')

        # Extract filename prefix by removing any extensions
        if '.' in new_file_name:
            new_file_name = new_file_name.split('.')[0]

        # Check that given filename does not match an existing filename in user's layout library
        user_files = ConvertedFile.objects.filter(user=self.instance.user)
        if user_files.filter(file_name=new_file_name).exists():
            raise forms.ValidationError("File name must not match an existing file in your library.")
        
        return new_file_name

class UpdateStyleSettingsForm(forms.ModelForm):
    """
    Form class for updating an individual layout's style settings.
    
    This form provides fields for updating the border colors and widths of a layout's windows, doors, walls, and furniture. It also allows the user 
    to update the colors for sensor objects, cameras, navigation arrows, and calibration points. A user can also switch the layout's orientation between
    portrait and landscape.

    Methods:
        clean(): Validation method ensuring that all updated border widths are within the permitted values of 1 through 16.
    """
    class Meta:
        model = StyleSettings
        fields = ('wall_color', 'door_color', 'furniture_color', 'window_color',
                  'wall_width', 'door_width', 'furniture_width', 'window_width',
                  'sensor_label_color', 'camera_label_color', 'navigation_arrow_color', 'calibration_color',
                  'orientation')
        widgets = {
            'wall_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control, form-select'}),
            'door_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control, form-select'}),
            'furniture_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control, form-select'}),
            'window_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control, form-select'}),
            'sensor_label_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control, form-select'}),
            'camera_label_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control, form-select'}),
            'navigation_arrow_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control, form-select'}),
            'calibration_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control, form-select'}),
            # border widths
            'wall_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 1, 'max': 16}),
            'door_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 1, 'max': 16}),
            'furniture_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 1, 'max': 16}),
            'window_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 1, 'max': 16}),
            }
        
    # Validate data when form is saved
    def clean(self):
            # Get data from the form
            cleaned_data = super().clean()
            wall_width = cleaned_data.get('wall_width')
            door_width = cleaned_data.get('door_width')
            furniture_width = cleaned_data.get('furniture_width')
            window_width = cleaned_data.get('window_width')

            # Check that all TextInput fields for widths contain valid number values between 1 and 16
            if wall_width is not None and (wall_width < 1 or wall_width > 16):
                 raise ValidationError('Wall width must be between 1 and 16.')
            if door_width is not None and (door_width < 1 or door_width > 16):
                raise ValidationError('Door width must be between 1 and 16.')
            if furniture_width is not None and (furniture_width < 1 or furniture_width > 16):
                raise ValidationError('Furniture width must be between 1 and 16.')
            if window_width is not None and (window_width < 1 or window_width > 16):
                raise ValidationError('Window width must be between 1 and 16.')

            return cleaned_data

class UpdateDefaultStyleSettingsForm(ModelForm):
    """
    Form class for updating a user's default style settings.
    
    This form provides fields for updating the border colors and widths for furniture, windows, doors, and walls along with the colors for sensors,
    cameras, navigation arrows, and calibration points for all future layouts generated by a user. It achieves this by updating the DefaultStyleSettings
    object associated with the current user.

    Methods:
        clean(): Validation method ensuring that all updated border widths are within the permitted values of 1 through 16.
    """
    class Meta:
        model = DefaultStyleSettings
        fields = ('wall_color', 'door_color', 'furniture_color', 'window_color',
                  'wall_width', 'door_width', 'furniture_width', 'window_width',
                  'sensor_label_color', 'camera_label_color', 'navigation_arrow_color', 'calibration_color')
        widgets = {
            'wall_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control, form-select'}),
            'door_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control, form-select'}),
            'furniture_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-, form-select'}),
            'window_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control, form-select'}),
            'sensor_label_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control, form-select'}),
            'camera_label_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control, form-select'}),
            'navigation_arrow_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control, form-select'}),
            'calibration_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control, form-select'}),
            # border widths
            'wall_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 1, 'max': 16}),
            'door_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 1, 'max': 16}),
            'furniture_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 1, 'max': 16}),
            'window_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 1, 'max': 16}),
        }

    # Validate data when form is saved
    def clean(self):
            cleaned_data = super().clean()
            wall_width = cleaned_data.get('wall_width')
            door_width = cleaned_data.get('door_width')
            furniture_width = cleaned_data.get('furniture_width')
            window_width = cleaned_data.get('window_width')
            # Check that all TextInput fields for widths contain valid number values between 1 and 16
            if wall_width is not None and (wall_width < 1 or wall_width > 16):
                 raise ValidationError('Wall width must be between 1 and 16.')
            if door_width is not None and (door_width < 1 or door_width > 16):
                raise ValidationError('Door width must be between 1 and 16.')
            if furniture_width is not None and (furniture_width < 1 or furniture_width > 16):
                raise ValidationError('Furniture width must be between 1 and 16.')
            if window_width is not None and (window_width < 1 or window_width > 16):
                raise ValidationError('Window width must be between 1 and 16.')

            return cleaned_data

class LabelForm(forms.Form):
    """
    Form class for updating the location of a specific label.

    This form is displayed for each label on a layout's Edit Style page. It allows a user to choose from 'left', 'right', 'above', or 'below' to modify the
    location of a label for a camera/nav arrow/sensor/calibration object.

    """
    location = forms.ChoiceField(choices=Label.LABEL_LOCATIONS, widget=forms.Select(attrs={'class': 'form-control form-select'}))