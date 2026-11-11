from django.conf import settings
from django.db import models, transaction
from django.urls import reverse


class Board(models.Model):
    """Tablica dyskusyjna, np. /random/, /tech/."""

    slug = models.SlugField('skrot', max_length=20, unique=True)
    name = models.CharField('nazwa', max_length=100)
    description = models.CharField('opis', max_length=255, blank=True)

    nsfw = models.BooleanField('NSFW', default=False)

    max_threads = models.PositiveIntegerField(
        'maks. wątków na tablicy', default=150,
        help_text='Najstarsze wątki powyżej tego limitu trafiają do archiwum.',
    )

    # Licznik uzywany do przydzielania kolejnych Post.post_number w obrebie tablicy
    post_counter = models.PositiveBigIntegerField('licznik postow', default=0)

    is_active = models.BooleanField('aktywna', default=True)
    created_at = models.DateTimeField('utworzono', auto_now_add=True)

    class Meta:
        verbose_name = 'tablica'
        verbose_name_plural = 'tablice'
        ordering = ['slug']

    def __str__(self):
        return f'/{self.slug}/ - {self.name}'

    def get_absolute_url(self):
        return reverse('boards:board_detail', kwargs={'slug': self.slug})

    def next_post_number(self):
        """Atomowo zwraca kolejny numer postu w obrebie tej tablicy."""
        with transaction.atomic():
            board = Board.objects.select_for_update().get(pk=self.pk)
            board.post_counter = models.F('post_counter') + 1
            board.save(update_fields=['post_counter'])
            board.refresh_from_db(fields=['post_counter'])
            self.post_counter = board.post_counter
            return board.post_counter


class Thread(models.Model):
    """Wątek na tablicy. Pierwszy Post (is_op=True) jest tresciu OP-a."""

    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name='threads', verbose_name='tablica',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='threads', verbose_name='autor',
    )
    title = models.CharField('tytul', max_length=255)

    pinned = models.BooleanField('przypiety', default=False)
    locked = models.BooleanField('zablokowany', default=False)
    archived = models.BooleanField('zarchiwizowany', default=False)

    created_at = models.DateTimeField('utworzono', auto_now_add=True)
    bumped_at = models.DateTimeField('ostatni bump', auto_now_add=True)

    class Meta:
        verbose_name = 'wątek'
        verbose_name_plural = 'wątki'
        ordering = ['-pinned', '-bumped_at']
        indexes = [
            models.Index(fields=['board', 'bumped_at']),
        ]

    def __str__(self):
        return f'{self.title} (/{self.board.slug}/)'

    def get_absolute_url(self):
        return reverse('boards:thread_detail', kwargs={'board_slug': self.board.slug, 'pk': self.pk})

    def bump(self):
        """Przesuwa wątek na szczyt katalogu po nowej odpowiedzi."""
        self.bumped_at = models.functions.Now()
        self.save(update_fields=['bumped_at'])


class Post(models.Model):
    """Pojedynczy wpis: OP (pierwszy w wątku) lub odpowiedz."""

    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name='posts', verbose_name='wątek',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='posts', verbose_name='autor',
    )

    # Numer postu unikalny w obrebie calej tablicy (jak na 4chanie), nie wątku
    post_number = models.PositiveBigIntegerField('numer postu', editable=False)

    content = models.TextField('tresc')
    is_op = models.BooleanField('jest pierwszym postem wątku', default=False)

    # Odpowiednik "sage" - odpowiedz nie podbija wątku na liscie
    no_bump = models.BooleanField('nie podbijaj wątku', default=False)

    created_at = models.DateTimeField('utworzono', auto_now_add=True)
    edited_at = models.DateTimeField('edytowano', null=True, blank=True)

    # Hash adresu IP - pomocniczy przy wykrywaniu multikont/spamu, nie zastepuje konta
    ip_hash = models.CharField('hash IP', max_length=64, blank=True)

    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posty'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['thread', 'created_at']),
            models.Index(fields=['post_number']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['post_number'], name='unique_post_number'),
        ]

    def __str__(self):
        return f'#{self.post_number} ({self.author})'

    def get_absolute_url(self):
        return f'{self.thread.get_absolute_url()}#p{self.post_number}'

    def save(self, *args, **kwargs):
        if self.post_number is None or self.post_number == 0:
            self.post_number = self.thread.board.next_post_number()
        super().save(*args, **kwargs)


class Attachment(models.Model):
    """Zdjecie lub GIF dołączony do postu."""

    class Kind(models.TextChoices):
        IMAGE = 'image', 'Obraz'
        GIF = 'gif', 'GIF'

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='attachments', verbose_name='post',
    )

    file = models.ImageField('plik', upload_to='attachments/%Y/%m/')
    thumbnail = models.ImageField('miniatura', upload_to='thumbnails/%Y/%m/', blank=True)

    kind = models.CharField('typ', max_length=10, choices=Kind.choices, default=Kind.IMAGE)
    original_filename = models.CharField('oryginalna nazwa', max_length=255, blank=True)
    content_type = models.CharField('typ MIME', max_length=100, blank=True)
    width = models.PositiveIntegerField('szerokosc', null=True, blank=True)
    height = models.PositiveIntegerField('wysokosc', null=True, blank=True)
    size_bytes = models.PositiveIntegerField('rozmiar (bajty)', null=True, blank=True)

    created_at = models.DateTimeField('utworzono', auto_now_add=True)

    class Meta:
        verbose_name = 'zalacznik'
        verbose_name_plural = 'zalaczniki'

    def __str__(self):
        return self.original_filename or self.file.name
