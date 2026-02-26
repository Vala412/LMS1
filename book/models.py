from django.db import models
from author.models import Author
from genre.models import Genre
from django.core.validators import MinValueValidator, RegexValidator

# Create your models here

class Book(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    genres = models.ManyToManyField(Genre, related_name='books')
    pages = models.IntegerField(validators=[MinValueValidator(1)])
    published_date = models.DateField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    isbn = models.CharField(
        max_length=13,
        unique=True,
        help_text='Enter 13 digit ISBN',
        validators=[
            RegexValidator(r'^\d{13}$', message='ISBN must be exactly 13 digits')
        ]
    )
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)

    class Meta:
        ordering = ['title', '-created_date']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['published_date']),
            models.Index(fields=['isbn']),
            # models.Index(fields=['author'])
        ]

    def __str__(self):
        return self.title