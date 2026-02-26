from django.contrib import admin
from .models import Book

# Register your models here.

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date')
    list_filter = ('author', 'genres', 'published_date')
    search_fields = ('title', 'author__name', 'genres__name')


admin.site.register(Book, BookAdmin)