from django.db import models
from django.utils.text import slugify
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError

# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, max_length=200, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        # constraints = [
        #     UniqueConstraint(
        #         Lower('name'), 
        #         name='genre_name_unique_case_insensitive'
        #     ),
        # ]

    
    def save(self, *args, **kwargs):
        # Generate the slug from the name in lowercase
        self.slug = slugify(self.name)
        # print(self.slug, 'hello123')

        if not self.pk: # only check for new objects
            existing_genres = Genre.objects.filter(slug=self.slug)
            if existing_genres.exists():
                raise ValidationError('Genre with this name already exists.')
        super(Genre, self).save()
        

    def __str__(self):
        return self.name