from django.contrib import admin
from .models import Author, Profile
# Register your models here.

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'profile')
    list_filter = ('name', 'birth_date', 'profile')
    search_fields = ('name', 'birth_date')


admin.site.register(Author, AuthorAdmin)
admin.site.register(Profile)