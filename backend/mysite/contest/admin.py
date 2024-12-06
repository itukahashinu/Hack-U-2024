from django.contrib import admin
from .models import Theme, Idea

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date')
    search_fields = ('title',)

@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'theme', 'created_at')
    search_fields = ('title', 'author__username')
    list_filter = ('theme',)
