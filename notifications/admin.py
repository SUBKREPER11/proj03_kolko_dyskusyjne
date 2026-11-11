from django.contrib import admin

from .models import Notification, Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'thread', 'created_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'kind', 'is_read', 'email_sent', 'created_at')
    list_filter = ('kind', 'is_read', 'email_sent')
