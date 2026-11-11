from django.contrib import admin

from .models import Attachment, Board, Post, Thread


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0


class PostInline(admin.TabularInline):
    model = Post
    extra = 0
    fields = ('post_number', 'author', 'is_op', 'content', 'created_at')
    readonly_fields = ('post_number', 'created_at')
    show_change_link = True


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'nsfw', 'is_active', 'max_threads', 'post_counter')
    search_fields = ('slug', 'name')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'board', 'author', 'pinned', 'locked', 'archived', 'bumped_at')
    list_filter = ('board', 'pinned', 'locked', 'archived')
    search_fields = ('title',)
    inlines = [PostInline]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('post_number', 'thread', 'author', 'is_op', 'no_bump', 'created_at')
    list_filter = ('is_op', 'no_bump')
    search_fields = ('content',)
    readonly_fields = ('post_number',)
    inlines = [AttachmentInline]
