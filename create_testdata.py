import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from django.contrib.auth.models import User, Group
from author.models import Author, Profile
from book.models import Book
from genre.models import Genre

# Create normal user
user1, created = User.objects.get_or_create(
    username='john_student',
    defaults={'email': 'john@library.local'}
)
if created:
    user1.set_password('password123')
    user1.save()
    Profile.objects.get_or_create(user=user1)
    print(f"Created normal user: john_student")
else:
    print(f"User john_student already exists")

# Create staff/librarian user
user2, created = User.objects.get_or_create(
    username='alice_librarian',
    defaults={'email': 'alice@library.local', 'is_staff': True}
)
if created:
    user2.set_password('password123')
    user2.save()
    Profile.objects.get_or_create(user=user2)
    print(f"Created staff user: alice_librarian")
else:
    print(f"User alice_librarian already exists")

# Create test authors
author1, created = Author.objects.get_or_create(
    name='George R.R. Martin',
    defaults={'birth_date': '1948-09-20'}
)
if created:
    print(f"Created author: George R.R. Martin")
    
author2, created = Author.objects.get_or_create(
    name='J.K. Rowling',
    defaults={'birth_date': '1965-07-31'}
)
if created:
    print(f"Created author: J.K. Rowling")

# Create test genres
fantasy, _ = Genre.objects.get_or_create(name='Fantasy')
sci_fi, _ = Genre.objects.get_or_create(name='Science Fiction')

# Create test books
book1, created = Book.objects.get_or_create(
    isbn='9780553103547',
    defaults={
        'title': 'A Game of Thrones',
        'author': author1,
        'description': 'The opening book of the series A Song of Ice and Fire',
        'pages': 694,
        'published_date': '1996-08-01',
        'total_copies': 3,
        'available_copies': 3,
    }
)
if created:
    book1.genres.add(fantasy)
    print(f"Created book: A Game of Thrones")

book2, created = Book.objects.get_or_create(
    isbn='9780747532699',
    defaults={
        'title': 'Harry Potter and the Philosopher\'s Stone',
        'author': author2,
        'description': 'The first book in the Harry Potter series',
        'pages': 223,
        'published_date': '1997-06-26',
        'total_copies': 5,
        'available_copies': 5,
    }
)
if created:
    book2.genres.add(fantasy)
    print(f"Created book: Harry Potter and the Philosopher's Stone")

print("\n✅ Test data ready!")
