from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """Wlasny model uzytkownika.

    Logowanie jest wymagane do pisania - w calym serwisie nie ma postow
    anonimowych, dlatego kazdy Post/Thread ma wymagany FK do tego modelu.
    """

    class Theme(models.TextChoices):
        LIGHT = 'light', 'Jasny'
        DARK = 'dark', 'Ciemny'

    email = models.EmailField('adres e-mail', unique=True)
    email_verified = models.BooleanField('e-mail zweryfikowany', default=False)

    avatar = models.ImageField('avatar', upload_to='avatars/%Y/%m/', blank=True)
    bio = models.CharField('o mnie', max_length=500, blank=True)
    theme = models.CharField('motyw', max_length=10, choices=Theme.choices, default=Theme.LIGHT)

    created_at = models.DateTimeField('utworzono', auto_now_add=True)

    class Meta:
        verbose_name = 'uzytkownik'
        verbose_name_plural = 'uzytkownicy'

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'username': self.username})
