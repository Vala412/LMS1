from django.contrib import admin
from .models import Genre
from .forms import GenreForm
# Register your models here.
class GenreAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    # readonly_fields = ('slug',)




admin.site.register(Genre, GenreAdmin)