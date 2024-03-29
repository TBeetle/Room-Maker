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
    old_password = forms.CharField(label="Old Password", widget=forms.PasswordInput, required=False)
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['email']
        
    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 or new_password2:
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
    new_file_name = forms.CharField(label='New file name', max_length=48, required=False)

    class Meta:
        model = ConvertedFile
        fields = ['new_file_name']

    def clean_new_file_name(self):
        new_file_name = self.cleaned_data['new_file_name']
        # Cleaning data:
        new_file_name = new_file_name.replace(' ', '_')
        # Extract filename prefix without extension
        if '.' in new_file_name:
            new_file_name = new_file_name.split('.')[0]
        # Check unique filename
        user_files = ConvertedFile.objects.filter(user=self.instance.user)
        if user_files.filter(file_name=new_file_name).exists():
            raise forms.ValidationError("File name must not match an existing file in your library.")
        return new_file_name


class UpdateStyleSettingsForm(ModelForm):
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
            'wall_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 2, 'max': 12}),
            'door_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 2, 'max': 12}),
            'furniture_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 2, 'max': 12}),
            'window_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 2, 'max': 12}),
            }

class UpdateDefaultStyleSettingsForm(ModelForm):
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
            'wall_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 2, 'max': 12}),
            'door_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 2, 'max': 12}),
            'furniture_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 2, 'max': 12}),
            'window_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 2, 'max': 12}),
        }

class LabelForm(forms.Form):
    location = forms.ChoiceField(choices=Label.LABEL_LOCATIONS, widget=forms.Select(attrs={'class': 'form-control form-select'}))
    # x_coordinate = forms.CharField(label="X Coordinate", widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 0, 'max': 250}))
    # y_coordinate = forms.CharField(label="Y Coordinate", widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 0, 'max': 250}))