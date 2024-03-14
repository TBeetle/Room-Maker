from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import StyleSettings, DefaultStyleSettings, ConvertedFile

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
            if not old_password:
                self.add_error('old_password', 'Please enter your old password.')
            else:
                user = self.instance
                if not user.check_password(old_password):
                    self.add_error('old_password', 'The old password is incorrect.')
        
        if new_password1 != new_password2:
            self.add_error('new_password2', 'The two password fields didn’t match.')
        
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
            raise forms.ValidationError("File name must be unique")

        return new_file_name


class UpdateStyleSettingsForm(ModelForm):
    class Meta:
        model = StyleSettings
        fields = ('wall_color', 'door_color', 'furniture_color', 'window_color',
                  'wall_width', 'door_width', 'furniture_width', 'window_width',
                  'sensor_label_color', 'camera_label_color', 'navigation_arrow_color', 'calibration_color',
                  'meta_title', 'meta_date', 'meta_location')
        widgets = {
            'wall_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control'}),
            'door_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control'}),
            'furniture_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control'}),
            'window_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control'}),
            'sensor_label_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control'}),
            'camera_label_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control'}),
            'navigation_arrow_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control'}),
            'calibration_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control'}),
            # border widths
            'wall_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 2, 'max': 12}),
            'door_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 2, 'max': 12}),
            'furniture_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 2, 'max': 12}),
            'window_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 2, 'max': 12}),
            # meta data styling
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_date': forms.DateInput(attrs={'class': 'form-control'}),
            'meta_location': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UpdateDefaultStyleSettingsForm(ModelForm):
    class Meta:
        model = DefaultStyleSettings
        fields = ('wall_color', 'door_color', 'furniture_color', 'window_color',
                  'wall_width', 'door_width', 'furniture_width', 'window_width',
                  'sensor_label_color', 'camera_label_color', 'navigation_arrow_color', 'calibration_color')
        widgets = {
            'wall_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control'}),
            'door_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control'}),
            'furniture_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control'}),
            'window_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control'}),
            'sensor_label_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control'}),
            'camera_label_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control'}),
            'navigation_arrow_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control'}),
            'calibration_color': forms.Select(choices=DefaultStyleSettings.COLOR_CHOICES, attrs={'class': 'form-control'}),
            # border widths
            'wall_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 2, 'max': 12}),
            'door_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 2, 'max': 12}),
            'furniture_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 2, 'max': 12}),
            'window_width': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 2, 'max': 12}),
        }

class LabelForm(forms.Form):
    x_coordinate = forms.CharField(label="X Coordinate", widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 0, 'max': 250}))
    y_coordinate = forms.CharField(label="Y Coordinate", widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'min': 0, 'max': 250}))