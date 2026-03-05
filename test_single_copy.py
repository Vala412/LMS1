"""Test exclusive single-copy lending system."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from django.contrib.auth.models import User
from book.models import Book, BookIssue
from book.services import issue_book_to_user, return_book
from book.exceptions import BookNotAvailableException

print("=" * 70)
print("🔒 TESTING EXCLUSIVE SINGLE-COPY LENDING SYSTEM")
print("=" * 70)

# Get test users
student1 = User.objects.get(username='john_student')
student2, created = User.objects.get_or_create(
    username='jane_student',
    defaults={'email': 'jane@library.local'}
)
if created:
    student2.set_password('password123')
    student2.save()
    from author.models import Profile
    Profile.objects.get_or_create(user=student2)

# Create a SINGLE-COPY book
single_copy_book, created = Book.objects.get_or_create(
    isbn='9780747532700',
    defaults={
        'title': 'The Hobbit',
        'author': Book.objects.first().author,
        'description': 'A fantasy adventure',
        'pages': 310,
        'published_date': '1937-09-21',
        'total_copies': 1,  # ⭐ ONLY 1 COPY
        'available_copies': 1,
    }
)

print(f"\n📖 Book Setup (Single Copy):")
print(f"  Title: {single_copy_book.title}")
print(f"  Total copies: {single_copy_book.total_copies}")
print(f"  Available: {single_copy_book.available_copies}")
print(f"  Status: Can be issued")

print(f"\n👥 Users:")
print(f"  Student 1: {student1.username}")
print(f"  Student 2: {student2.username}")

# Test 1: First user issues the single-copy book
print(f"\n✅ Test 1: First user issues the single-copy book")
try:
    issue1 = issue_book_to_user(student1, single_copy_book.id)
    single_copy_book.refresh_from_db()
    
    print(f"   ✓ {student1.username} issued '{single_copy_book.title}'")
    print(f"   ✓ Due date: {issue1.due_date}")
    print(f"   ✓ Available copies now: {single_copy_book.available_copies}")
    
    assert single_copy_book.available_copies == 0, "Available copies should be 0"
    print(f"   ✓ Book is now EXCLUSIVELY held by {student1.username}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Test 2: Second user tries to issue (should fail)
print(f"\n✅ Test 2: Second user tries to issue (should be blocked)")
try:
    try:
        issue2 = issue_book_to_user(student2, single_copy_book.id)
        print(f"   ✗ FAILED: Should have blocked {student2.username}")
    except BookNotAvailableException as e:
        print(f"   ✓ Correctly blocked: {e}")
        print(f"   ✓ {student2.username} cannot access book while {student1.username} has it")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Test 3: First user returns the book
print(f"\n✅ Test 3: First user returns the book")
try:
    return_book(issue1)
    single_copy_book.refresh_from_db()
    
    print(f"   ✓ {student1.username} returned '{single_copy_book.title}'")
    print(f"   ✓ Available copies restored: {single_copy_book.available_copies}")
    
    assert single_copy_book.available_copies == 1, "Available copies should be 1 again"
    print(f"   ✓ Book is now available again for others")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Test 4: Second user can now issue
print(f"\n✅ Test 4: Second user can now issue the book")
try:
    issue2 = issue_book_to_user(student2, single_copy_book.id)
    single_copy_book.refresh_from_db()
    
    print(f"   ✓ {student2.username} issued '{single_copy_book.title}'")
    print(f"   ✓ Due date: {issue2.due_date}")
    print(f"   ✓ Available copies now: {single_copy_book.available_copies}")
    
    assert single_copy_book.available_copies == 0, "Available copies should be 0"
    print(f"   ✓ Book is now EXCLUSIVELY held by {student2.username}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Test 5: First user cannot issue while student2 has it
print(f"\n✅ Test 5: First user cannot issue while student2 has it")
try:
    try:
        issue_book_to_user(student1, single_copy_book.id)
        print(f"   ✗ FAILED: Should have blocked {student1.username}")
    except BookNotAvailableException as e:
        print(f"   ✓ Correctly blocked: {e}")
        print(f"   ✓ {student1.username} cannot issue - {student2.username} has exclusive access")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Cleanup
return_book(issue2)

# Test 6: Multiple copies - concurrent access
print(f"\n✅ Test 6: Multiple-copy book allows concurrent access")
try:
    multi_copy, created = Book.objects.get_or_create(
        isbn='9780747532701',
        defaults={
            'title': 'The Lord of the Rings',
            'author': Book.objects.first().author,
            'description': 'Epic fantasy',
            'pages': 1178,
            'published_date': '1954-07-29',
            'total_copies': 3,  # ⭐ 3 COPIES
            'available_copies': 3,
        }
    )
    
    print(f"   ✓ Created book with 3 copies")
    
    # Both users can issue the same multi-copy book
    issue_m1 = issue_book_to_user(student1, multi_copy.id)
    multi_copy.refresh_from_db()
    print(f"   ✓ {student1.username} issued (Available: {multi_copy.available_copies})")
    
    issue_m2 = issue_book_to_user(student2, multi_copy.id)
    multi_copy.refresh_from_db()
    print(f"   ✓ {student2.username} also issued (Available: {multi_copy.available_copies})")
    
    assert multi_copy.available_copies == 1, "1 copy should remain available"
    print(f"   ✓ Both users can hold different copies simultaneously")
    
    # Cleanup
    return_book(issue_m1)
    return_book(issue_m2)
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n" + "=" * 70)
print("✅ EXCLUSIVE SINGLE-COPY LENDING TESTS COMPLETE")
print("=" * 70)

print(f"""
📌 KEY INSIGHT:

The system automatically implements exclusive lending:

  SINGLE-COPY BOOK (total_copies=1):
    ✓ Only 1 user can hold it at a time
    ✓ Once issued, available_copies = 0
    ✓ Others blocked with BookNotAvailableException
    ✓ Available again when returned

  MULTI-COPY BOOK (total_copies=N, N>1):
    ✓ Multiple users can hold it simultaneously
    ✓ Available only if available_copies > 0
    ✓ Each issue decreases available_copies
    ✓ Each return increases available_copies

🔧 TO MARK A BOOK AS SINGLE-COPY:
    book = Book.objects.get(id=X)
    book.total_copies = 1
    book.available_copies = 1
    book.save()

🔍 CHECK IF A BOOK IS AVAILABLE:
    book.available_copies > 0  # User can issue
    book.available_copies == 0 # Book is fully issued (no copies left)
""")
