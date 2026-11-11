from django.conf import settings
from django.db import models


class Subscription(models.Model):
    """Obserwowanie wątku - podstawa powiadomien (Etap 5)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='subscriptions', verbose_name='uzytkownik',
    )
    thread = models.ForeignKey(
        'boards.Thread', on_delete=models.CASCADE,
        related_name='subscriptions', verbose_name='wątek',
    )
    created_at = models.DateTimeField('utworzono', auto_now_add=True)

    class Meta:
        verbose_name = 'obserwowany wątek'
        verbose_name_plural = 'obserwowane wątki'
        constraints = [
            models.UniqueConstraint(fields=['user', 'thread'], name='unique_subscription'),
        ]

    def __str__(self):
        return f'{self.user} obserwuje {self.thread}'


class Notification(models.Model):
    """Powiadomienie uzytkownika (np. odpowiedz na jego post)."""

    class Kind(models.TextChoices):
        REPLY = 'reply', 'Odpowiedz na post'
        MENTION = 'mention', 'Wzmianka (>>id)'
        THREAD_REPLY = 'thread_reply', 'Nowa odpowiedz w obserwowanym wątku'
        MOD_ACTION = 'mod_action', 'Akcja moderacyjna'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications', verbose_name='odbiorca',
    )
    kind = models.CharField('typ', max_length=20, choices=Kind.choices)

    source_post = models.ForeignKey(
        'boards.Post', on_delete=models.CASCADE, null=True, blank=True,
        related_name='+', verbose_name='powiazany post',
    )

    is_read = models.BooleanField('przeczytane', default=False)
    email_sent = models.BooleanField('e-mail wyslany', default=False)

    created_at = models.DateTimeField('utworzono', auto_now_add=True)

    class Meta:
        verbose_name = 'powiadomienie'
        verbose_name_plural = 'powiadomienia'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f'{self.get_kind_display()} dla {self.recipient}'
