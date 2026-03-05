"""
Practical examples and setup for exclusive single-copy lending.
Run: python manage.py shell < examples_single_copy.py
Or copy-paste commands one by one.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from django.contrib.auth.models import User
from book.models import Book, BookIssue
from book.services import issue_book_to_user, return_book
from datetime import date

print("\n" + "=" * 70)
print("📚 EXCLUSIVE SINGLE-COPY LENDING - PRACTICAL EXAMPLES")
print("=" * 70)

# ============================================================================
# EXAMPLE 1: View all books and their "availability"
# ============================================================================
print("\n📖 EXAMPLE 1: Check all books' copy status")
print("-" * 70)

books = Book.objects.all()
for book in books:
    status = "🔒 SINGLE-COPY" if book.total_copies == 1 else f"📚 MULTI-COPY ({book.total_copies})"
    availability = "✅ AVAILABLE" if book.available_copies > 0 else "❌ ALL ISSUED"
    print(f"{book.id:2d}. {book.title:30s} | {status:20s} | {availability:15s} ({book.available_copies}/{book.total_copies})")

# ============================================================================
# EXAMPLE 2: Convert a multi-copy book to single-copy
# ============================================================================
print("\n\n🔄 EXAMPLE 2: Convert a book from multi-copy to single-copy")
print("-" * 70)

try:
    book = Book.objects.first()  # Get any book
    print(f"Selected: '{book.title}'")
    print(f"  Before: total_copies = {book.total_copies}, available = {book.available_copies}")
    
    # Convert to single-copy
    book.total_copies = 1
    book.available_copies = 1
    book.save()
    
    print(f"  After:  total_copies = {book.total_copies}, available = {book.available_copies}")
    print(f"  ✓ Now this is an EXCLUSIVE SINGLE-COPY book!")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ============================================================================
# EXAMPLE 3: Convert a single-copy book back to multi-copy
# ============================================================================
print("\n\n🔄 EXAMPLE 3: Convert a single-copy book back to multi-copy")
print("-" * 70)

try:
    books_single = Book.objects.filter(total_copies=1)
    if books_single.exists():
        book = books_single.first()
        print(f"Selected: '{book.title}'")
        print(f"  Before: total_copies = {book.total_copies}, available = {book.available_copies}")
        
        # Convert to multi-copy (3 copies)
        book.total_copies = 3
        book.available_copies = 3
        book.save()
        
        print(f"  After:  total_copies = {book.total_copies}, available = {book.available_copies}")
        print(f"  ✓ Now this book has 3 copies available!")
    else:
        print("  ℹ️  No single-copy books to convert")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ============================================================================
# EXAMPLE 4: See who has which books currently
# ============================================================================
print("\n\n👥 EXAMPLE 4: See current loans (who has what)")
print("-" * 70)

active_issues = BookIssue.objects.filter(is_returned=False).select_related('user', 'book')

if active_issues.exists():
    for issue in active_issues:
        days_remaining = (issue.due_date - date.today()).days
        status = "⏰ DUE SOON" if days_remaining < 3 else "✓ ON TIME"
        print(f"  👤 {issue.user.username:15s} → {issue.book.title:30s} | Due: {issue.due_date} ({status})")
else:
    print("  ℹ️  No active loans")

# ============================================================================
# EXAMPLE 5: Find blocking situations (useful for librarians)
# ============================================================================
print("\n\n🚫 EXAMPLE 5: Find books that are fully issued (blocking users)")
print("-" * 70)

fully_issued = Book.objects.filter(available_copies=0)

if fully_issued.exists():
    print(f"  Found {fully_issued.count()} book(s) with NO copies available:")
    for book in fully_issued:
        type_label = "🔒 SINGLE" if book.total_copies == 1 else f"📚 MULTI ({book.total_copies})"
        # Find who has it
        holder = BookIssue.objects.filter(book=book, is_returned=False).first()
        if holder:
            print(f"    • {book.title:30s} ({type_label}) - Held by: {holder.user.username}")
        else:
            print(f"    • {book.title:30s} ({type_label}) - ERROR: No holder found!")
else:
    print("  ✓ All books have at least 1 copy available!")

# ============================================================================
# EXAMPLE 6: Generate a report card for all books
# ============================================================================
print("\n\n📋 EXAMPLE 6: Full inventory report")
print("-" * 70)

all_books = Book.objects.all()
total_books = all_books.count()
single_copy = all_books.filter(total_copies=1).count()
multi_copy = total_books - single_copy
fully_available = all_books.filter(available_copies__gt=0).count()
fully_issued = all_books.filter(available_copies=0).count()

print(f"  Total Books: {total_books}")
print(f"   - Single-Copy (🔒): {single_copy}")
print(f"   - Multi-Copy (📚): {multi_copy}")
print(f"\n  Availability:")
print(f"   - Fully Available (≥1 copy): {fully_available}")
print(f"   - Fully Issued (0 copies): {fully_issued}")

# ============================================================================
# EXAMPLE 7: Commands to run from terminal
# ============================================================================
print("\n\n⚙️  EXAMPLE 7: Shell commands (run in terminal)")
print("-" * 70)
print("""
  # View available management command
  python manage.py configure_book_copies --help
  
  # Make book ID 1 a single-copy
  python manage.py configure_book_copies 1 --single
  
  # Make book ID 2 have 5 copies
  python manage.py configure_book_copies 2 --multi 5
  
  # Direct shell scripting:
  python manage.py shell
  from book.models import Book
  b = Book.objects.get(id=1)
  b.total_copies = 1
  b.available_copies = 1
  b.save()
  
  # Check if book is single-copy:
  print(b.total_copies == 1)  # True = single-copy, False = multi-copy
""")

# ============================================================================
# EXAMPLE 8: Understand the blocking mechanism
# ============================================================================
print("\n\n🔒 EXAMPLE 8: How blocking works")
print("-" * 70)
print("""
  SINGLE-COPY BOOK:
    User A issues → available_copies = 0 → blocks all others
    User B tries → BookNotAvailableException ("no copies available")
    User A returns → available_copies = 1 → unblocks others
  
  Key insight: When available_copies = 0, NO ONE can issue
              regardless of who currently holds it.
  
  MULTI-COPY BOOK:
    Issue 1 → available_copies = n-1
    Issue 2 → available_copies = n-2
    ...
    Issue n → available_copies = 0 → blocks new issues
    Return 1 → available_copies = 1 → allows new issue
""")

print("\n" + "=" * 70)
print("✅ EXAMPLES COMPLETE")
print("=" * 70)
print("\n💡 Next steps:")
print("   1. Go to http://localhost:8000/admin/book/book/")
print("   2. Click any book to see the enhanced admin interface")
print("   3. Notice 'Copy Status' and 'Availability' columns")
print("   4. Use 'Inventory & Copies' section to change total_copies")
print("   5. Watch available_copies auto-update!\n")
