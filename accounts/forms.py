from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User

MAX_AVATAR_BYTES = 2 * 1024 * 1024


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label='Adres e-mail')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Konto z tym adresem e-mail już istnieje.')
        return email


class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'avatar', 'bio', 'theme')
        widgets = {'bio': forms.Textarea(attrs={'rows': 4})}

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Konto z tym adresem e-mail już istnieje.')
        return email

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'size') and avatar.size > MAX_AVATAR_BYTES:
            raise forms.ValidationError('Avatar może mieć maksymalnie 2 MB.')
        return avatar

    def save(self, commit=True):
        user = super().save(commit=False)
        if 'email' in self.changed_data:
            user.email_verified = False
        if commit:
            user.save()
        return user
