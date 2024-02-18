from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import StyleSettings

from django import forms
from django.forms import ModelForm

class AccountSettingsForm(forms.Form):
    email = forms.EmailField(label='Email:', widget=forms.EmailInput(attrs={'class': 'form-control'}), required=False)
    inputPassword1 = forms.CharField(label='Change Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    inputPassword2 = forms.CharField(label='Confirm Changes', widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    currentPassword = forms.CharField(label='Current Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))

    # Verify that passwords match
    def clean(self):
        cleaned_data = super().clean()
        password1 = self.cleaned_data.get('inputPassword1')
        password2 = self.cleaned_data.get('inputPassword2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data
    
    def clean_email(self): 
        old_email = self.user.email
        new_email = self.cleaned_data.get('email')
        if new_email and old_email and new_email==old_email:
            raise forms.ValidationError("Please enter an email that you have not used previously")
        return new_email
    
    # Ensure user confirms their current password before making account changes
    def clean_currentPassword(self):
        current_password = self.cleaned_data.get('currentPassword')
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Current password is incorrect.")
        return current_password
    
    def save(self, commit=True):
        email = self.cleaned_data['email']
        self.user.email = email
        if commit:
            self.user.save()
        return self.user

    def __init__(self, user, *args, **kwargs):
        # Get initial email passed from SettingsPage view
        user_email = kwargs.pop('initial', {}).get('email', '')
        super().__init__(*args, **kwargs)
        self.user = user  # Store user as attribute
        # Set placeholder attribute to user's current email
        self.fields['email'].widget.attrs['placeholder'] = user_email

    class Meta:
        model = User
        fields = ('email',)


class UpdateStyleSettingsForm(ModelForm):
    class Meta:
        model = StyleSettings
        fields = ('text_decoration', 'font_type', 'font_size', 'font_color',
                  'wall_color', 'door_color', 'furniture_color', 'window_color',
                  'wall_width', 'door_width', 'furniture_width', 'window_width')
        widgets = {
            'text_decoration': forms.Select(attrs={'class': 'form-control'}),
            'font_type': forms.Select(attrs={'class': 'form-control'}),
            'font_size': forms.NumberInput(attrs={'class':'form-control', 'type':'range',
                                             'min':2, 'max':12, 'step':1}),
            'font_color': forms.TextInput(attrs={'type': 'color'}),
            
            'wall_color': forms.TextInput(attrs={'type': 'color'}),
            'door_color': forms.TextInput(attrs={'type': 'color'}),
            'furniture_color': forms.TextInput(attrs={'type': 'color'}),
            'window_color': forms.TextInput(attrs={'type': 'color'}),

            'wall_width': forms.NumberInput(attrs={'class':'form-control', 'type':'range',
                                             'min':2, 'max':12, 'step':1}),
            'door_width': forms.NumberInput(attrs={'class':'form-control', 'type':'range',
                                             'min':2, 'max':12, 'step':1}),
            'furniture_width': forms.NumberInput(attrs={'class':'form-control', 'type':'range',
                                             'min':2, 'max':12, 'step':1}),
            'window_width': forms.NumberInput(attrs={'class':'form-control', 'type':'range',
                                             'min':2, 'max':12, 'step':1}),
        }