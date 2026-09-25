from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from urllib.parse import urlparse

class MovieForm(forms.ModelForm):

    def clean_trailer_url(self):
        url = self.cleaned_data['trailer_url']

        if url:
            parsed = urlparse(url)

            allowed_domains = [
                "youtube.com",
                "www.youtube.com",
                "youtu.be"
            ]

            if parsed.netloc not in allowed_domains:
                raise forms.ValidationError(
                    "Only YouTube URLs are allowed."
                )

        return url
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User  # If adding more profile fields, change to a Profile model
        fields = ['password']  # User can reset password