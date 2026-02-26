from django import forms
from .models import Book
import datetime

class BookModelForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        exclude = ['created_date']

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title) < 3:
            raise forms.ValidationError("Title is too short it must be at least 3 characters long")
        # case-insensitive uniqueness
        if title and Book.objects.filter(title__iexact=title).exists():
            raise forms.ValidationError("A book with this title already exists")
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description or len(description) < 10:
            raise forms.ValidationError("Description is too short")
        return description
    
    def clean_genres(self):
        genres = self.cleaned_data.get('genres')
        if not genres:
            raise forms.ValidationError('Select at lease one genre')
        return genres

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if isbn:
            if len(isbn) != 13:
                raise forms.ValidationError('ISBN must be exactly 13 characters long')
            if not isbn.isdigit():
                raise forms.ValidationError('ISBN must contain only digits')
            # uniqueness handled by model constraint but we can check for another record
            if Book.objects.filter(isbn=isbn).exists():
                raise forms.ValidationError('A book with this ISBN already exists')
        return isbn
    
    def clean_pages(self):
        pages = self.cleaned_data.get('pages')
        if pages is not None and pages <= 0:
            raise forms.ValidationError("Number of pages must be positive.")
        return pages
    
    def clean(self):
        cleaned_data = super().clean()
        pub_date = cleaned_data.get('published_date')
        image = cleaned_data.get('cover_image')

        if pub_date and pub_date > datetime.date.today():
            raise forms.ValidationError('Published date cannot be in the future')
        
        if image:
            if not image.name.endswith(('.jpg', '.png', '.jpeg')):
                raise forms.ValidationError("Image format .jpg, .png and .jpeg is allowed")
        
        return cleaned_data