from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User

from django import forms

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

