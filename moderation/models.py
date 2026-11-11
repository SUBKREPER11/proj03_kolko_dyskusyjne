from django.conf import settings
from django.db import models


class Report(models.Model):
    """Zgloszenie postu do moderacji."""

    class Reason(models.TextChoices):
        SPAM = 'spam', 'Spam'
        OFFTOPIC = 'offtopic', 'Nie na temat'
        ILLEGAL = 'illegal', 'Tresc nielegalna'
        HARASSMENT = 'harassment', 'Nękanie / obrazanie'
        OTHER = 'other', 'Inne'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Oczekujące'
        RESOLVED = 'resolved', 'Rozpatrzone'
        REJECTED = 'rejected', 'Odrzucone'

    post = models.ForeignKey(
        'boards.Post', on_delete=models.CASCADE, related_name='reports', verbose_name='post',
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='reports_made', verbose_name='zglaszajacy',
    )
    reason = models.CharField('powod', max_length=20, choices=Reason.choices)
    comment = models.CharField('komentarz', max_length=500, blank=True)

    status = models.CharField('status', max_length=10, choices=Status.choices, default=Status.PENDING)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reports_resolved', verbose_name='rozpatrzone przez',
    )

    created_at = models.DateTimeField('zgloszono', auto_now_add=True)
    resolved_at = models.DateTimeField('rozpatrzono', null=True, blank=True)

    class Meta:
        verbose_name = 'zgloszenie'
        verbose_name_plural = 'zgloszenia'
        ordering = ['-created_at']

    def __str__(self):
        return f'Zgloszenie postu #{self.post_id} ({self.get_reason_display()})'


class Ban(models.Model):
    """Ban konta (ewentualnie wsparty hashem IP przy wykrywaniu multikont)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='bans', verbose_name='uzytkownik',
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='bans_issued', verbose_name='wydany przez',
    )
    reason = models.CharField('powod', max_length=500)
    ip_hash = models.CharField('hash IP', max_length=64, blank=True)

    created_at = models.DateTimeField('wydano', auto_now_add=True)
    expires_at = models.DateTimeField('wygasa', null=True, blank=True, help_text='Puste = ban permanentny.')
    lifted_at = models.DateTimeField('zdjety', null=True, blank=True)

    class Meta:
        verbose_name = 'ban'
        verbose_name_plural = 'bany'
        ordering = ['-created_at']

    def __str__(self):
        return f'Ban: {self.user} ({self.reason[:40]})'

    def is_active(self):
        if self.lifted_at is not None:
            return False
        if self.expires_at is None:
            return True
        from django.utils import timezone
        return timezone.now() < self.expires_at


class ModAction(models.Model):
    """Log dzialan moderatorskich."""

    class Action(models.TextChoices):
        DELETE_POST = 'delete_post', 'Usunięcie postu'
        DELETE_THREAD = 'delete_thread', 'Usunięcie wątku'
        PIN_THREAD = 'pin_thread', 'Przypięcie wątku'
        LOCK_THREAD = 'lock_thread', 'Zablokowanie wątku'
        BAN_USER = 'ban_user', 'Ban użytkownika'
        LIFT_BAN = 'lift_ban', 'Zdjęcie bana'
        RESOLVE_REPORT = 'resolve_report', 'Rozpatrzenie zgloszenia'

    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='mod_actions', verbose_name='moderator',
    )
    action = models.CharField('akcja', max_length=20, choices=Action.choices)

    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='mod_actions_against', verbose_name='dotyczy uzytkownika',
    )
    target_post = models.ForeignKey(
        'boards.Post', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='mod_actions', verbose_name='dotyczy postu',
    )
    target_thread = models.ForeignKey(
        'boards.Thread', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='mod_actions', verbose_name='dotyczy wątku',
    )

    note = models.CharField('notatka', max_length=500, blank=True)
    created_at = models.DateTimeField('wykonano', auto_now_add=True)

    class Meta:
        verbose_name = 'akcja moderacyjna'
        verbose_name_plural = 'akcje moderacyjne'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_action_display()} przez {self.moderator}'
