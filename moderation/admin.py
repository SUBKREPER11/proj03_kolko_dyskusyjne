from django.contrib import admin

from .models import Ban, ModAction, Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('post', 'reason', 'status', 'reported_by', 'created_at')
    list_filter = ('status', 'reason')


@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    list_display = ('user', 'reason', 'issued_by', 'created_at', 'expires_at', 'lifted_at')
    list_filter = ('lifted_at',)


@admin.register(ModAction)
class ModActionAdmin(admin.ModelAdmin):
    list_display = ('action', 'moderator', 'target_user', 'target_post', 'target_thread', 'created_at')
    list_filter = ('action',)
