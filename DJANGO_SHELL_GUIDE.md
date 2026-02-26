# Django Shell Practice - Library Management System

This document contains practical ORM examples for the Library Management System.

## Starting Django Shell

```bash
python manage.py shell
```

## ✅ Create Operations

### Create an Author
```python
from author.models import Author
from django.contrib.auth.models import User

author = Author.objects.create(
    name="George R. R. Martin",
    birth_date="1948-09-20"
)
print(author)  # Output: George R. R. Martin
```

### Create Multiple Authors (bulk_create)
```python
authors = Author.objects.bulk_create([
    Author(name="Stephen King", birth_date="1947-09-21"),
    Author(name="J.K. Rowling", birth_date="1965-07-31"),
    Author(name="Isaac Asimov", birth_date="1920-01-02"),
])
print(f"Created {len(authors)} authors")
```

### Create a Genre
```python
from genre.models import Genre

fantasy = Genre.objects.create(
    name="Fantasy",
    description="Imaginative stories with magical elements"
)
print(fantasy)  # Output: Fantasy
```

### Create a Book
```python
from book.models import Book
from datetime import date

book = Book.objects.create(
    title="A Game of Thrones",
    description="The first book in the series",
    author=author,  # Use the George R.R. Martin author
    pages=694,
    published_date=date(1996, 8, 6),
    isbn="0553103547"
)
print(book)  # Output: A Game of Thrones
```

### Add Genres to a Book
```python
book.genres.add(fantasy)
book.genres.add(Genre.objects.get(name="Adventure"))
print(f"Book has {book.genres.count()} genres")
```

### Create User Profile
```python
from author.models import Profile

user = User.objects.create_user(
    username='george_martin',
    email='george@example.com',
    password='securepass123'
)

profile = Profile.objects.create(
    user=user,
    bio="Author of Game of Thrones series"
)

# Link profile to author
author.profile = profile
author.save()
```

## 🔍 Read Operations (Queries)

### Get a Single Object
```python
# Using get() - raises exception if not found
book = Book.objects.get(title="A Game of Thrones")

# Using get_object_or_404 safer in views
from django.shortcuts import get_object_or_404
book = get_object_or_404(Book, isbn="0553103547")
```

### Filter Multiple Objects
```python
# All books by an specific author
books_by_author = Book.objects.filter(author__name="George R. R. Martin")

# Books published after 2000
from datetime import date
recent_books = Book.objects.filter(published_date__gte=date(2000, 1, 1))

# Books in specific genre
fantasy_books = Book.objects.filter(genres__name="Fantasy")

# Case-insensitive title search
book = Book.objects.filter(title__icontains="thrones").first()
```

### Exclude Objects
```python
# All books NOT by George R.R. Martin
other_authors_books = Book.objects.exclude(author__name="George R. R. Martin")

# Books without cover images
books_no_image = Book.objects.filter(cover_image="")
books_with_image = Book.objects.exclude(cover_image="")
```

### Count & Aggregate
```python
# Total books
total = Book.objects.count()

# Total pages in all books
from django.db.models import Sum
total_pages = Book.objects.aggregate(Sum('pages'))['pages__sum']

# Books per author
from django.db.models import Count
author_book_counts = Author.objects.annotate(num_books=Count('books'))
for author in author_book_counts:
    print(f"{author.name}: {author.num_books} books")
```

### Ordering
```python
# Order by title ascending
books = Book.objects.all().order_by('title')

# Order by date descending
recent = Book.objects.all().order_by('-published_date')

# Order by multiple fields
ordered = Book.objects.order_by('author', '-published_date')
```

### Slicing (Pagination)
```python
# First 5 books
first_five = Book.objects.all()[:5]

# Skip first 10, take next 10
page_two = Book.objects.all()[10:20]

# Last book (if exists)
last_book = Book.objects.all().last()
```

### Optimized Queries (select_related, prefetch_related)
```python
# select_related for ForeignKey (JOIN operation)
books = Book.objects.select_related('author')
for book in books:
    # No extra queries - author already loaded
    print(f"{book.title} by {book.author.name}")

# prefetch_related for ManyToMany (multiple queries but efficient)
books = Book.objects.prefetch_related('genres')
for book in books:
    # genres loaded efficiently
    genres_list = list(book.genres.all())

# Combine both
books = Book.objects.select_related('author').prefetch_related('genres')

# Query optimization for reverse relations
authors = Author.objects.prefetch_related('books')
for author in authors:
    print(f"{author.name} wrote {author.books.count()} books")
```

### Complex Queries
```python
from django.db.models import Q

# OR queries using Q objects
fantasy_or_scifi = Book.objects.filter(
    Q(genres__name="Fantasy") | Q(genres__name="Science Fiction")
).distinct()

# AND & NOT
published_after_2000_no_image = Book.objects.filter(
    published_date__year__gte=2000
).filter(
    ~Q(cover_image="")  # NOT empty
)

# IN clause
book_ids = [1, 2, 3]
books = Book.objects.filter(id__in=book_ids)
```

### Distinct Results
```python
# Avoid duplicates when using ManyToMany filters
fantasy_authors = Author.objects.filter(
    books__genres__name="Fantasy"
).distinct()
```

## ✏️ Update Operations

### Update Single Object
```python
# Method 1: Modify and save
book = Book.objects.get(title="A Game of Thrones")
book.updated_at  # Auto-updated with auto_now=True
book.description = "Updated description"
book.save()

# Method 2: Update directly
Book.objects.filter(title="A Game of Thrones").update(
    updated_at=timezone.now(),
    pages=700
)
```

### Bulk Update
```python
# Update all books by an author
Book.objects.filter(author__name="Stephen King").update(
    pages=500  # WARNING: Sets all to 500
)
```

### Update Relationships
```python
# Change author of a book
book = Book.objects.get(title="A Game of Thrones")
new_author = Author.objects.get(name="J.K. Rowling")
book.author = new_author
book.save()

# Add genre to book
book.genres.add(Genre.objects.get(name="Drama"))

# Remove genre
book.genres.remove(fantasy)

# Clear all genres
book.genres.clear()

# Set multiple genres (replaces existing)
book.genres.set([fantasy, Genre.objects.get(name="Adventure")])
```

### Update User Profile
```python
profile = Profile.objects.get(user__username="george_martin")
profile.bio = "Legendary author of ASOIAF"
profile.save()
```

## ❌ Delete Operations

### Delete Single Object
```python
# Method 1: Delete instance
book = Book.objects.get(title="A Game of Thrones")
book.delete()
# Returns: (1, {'book.Book': 1})

# Method 2: Delete via queryset
Book.objects.filter(title="A Game of Thrones").delete()
```

### Delete Multiple Objects
```python
# Delete all books by an author
Book.objects.filter(author__name="Stephen King").delete()

# Delete with caution
Book.objects.filter(pages__lt=100).delete()  # Books with < 100 pages
```

### Delete with Cascading
```python
# Deleting author deletes related books (CASCADE)
author = Author.objects.get(name="George R. R. Martin")
author.delete()  # Also deletes all his books
```

### Remove from ManyToMany (without deleting)
```python
book = Book.objects.get(title="A Game of Thrones")
book.genres.remove(fantasy)  # Removes but doesn't delete genre
```

## 📊 Advanced Queries

### Group By (Aggregation)
```python
from django.db.models import Count, Avg

# Books per author
authors_with_count = Author.objects.annotate(
    book_count=Count('books'),
    avg_pages=Avg('books__pages')
)
for author in authors_with_count:
    print(f"{author.name}: {author.book_count} books, avg {author.avg_pages} pages")
```

### Raw SQL (when ORM isn't enough)
```python
from django.db import connection

books = Book.objects.raw(
    'SELECT * FROM book_book WHERE published_date > %s',
    [date(2000, 1, 1)]
)
```

### Values (returning dictionaries instead of model instances)
```python
# Get only specific fields
book_titles = Book.objects.values('title', 'author__name')
for item in book_titles:
    print(item)  # {'title': '...', 'author__name': '...'}

# Count distinct authors
distinct_authors = Book.objects.values('author').distinct().count()
```

### Check Existence
```python
# Check if book exists
exists = Book.objects.filter(isbn="0553103547").exists()
if exists:
    print("Found!")

# Count method
count = Book.objects.filter(author__name="Stephen King").count()
if count > 0:
    print(f"Found {count} books")
```

## 🧪 Testing Patterns

```python
# Clean queries before testing
Book.objects.all().delete()
Author.objects.all().delete()

# Create test data
test_author = Author.objects.create(name="Test Author")
test_book = Book.objects.create(
    title="Test Book",
    author=test_author,
    pages=100,
    published_date=date.today(),
    isbn="1234567890123"
)

# Assert relationships
assert test_book.author == test_author
assert test_book.author.books.count() == 1

# Clean up
test_book.delete()
test_author.delete()
```

## ⚡ Performance Tips

1. **Use select_related for ForeignKey**: Reduces N+1 queries
2. **Use prefetch_related for ManyToMany**: Efficient reverse lookups
3. **Use only() and defer()**: Load specific fields only
4. **Use values_list()**: When you don't need full objects
5. **Use exists()**: Instead of count() for existence checks
6. **Index frequently queried fields**: (Already done in model Meta)
7. **Batch operations**: Use bulk_create(), bulk_update()

```python
# Example of efficient query
books = Book.objects.select_related('author').prefetch_related('genres').filter(
    published_date__year=2020
).values_list('title', 'author__name').order_by('title')
```

## Further Reading

- [Django QuerySet API Reference](https://docs.djangoproject.com/en/5.2/ref/models/querysets/)
- [Database Access Optimization](https://docs.djangoproject.com/en/5.2/topics/db/optimization/)
