"""Test issue and return workflows to verify system functionality."""
import os
import django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from django.contrib.auth.models import User
from book.models import Book, BookIssue
from book.services import issue_book_to_user, return_book
from book.exceptions import (
    BookNotAvailableException,
    IssueLimitExceededException,
    InvalidReturnException,
)

print("=" * 60)
print("🧪 TESTING ISSUE/RETURN WORKFLOWS")
print("=" * 60)

# Get test users
student = User.objects.get(username='john_student')
librarian = User.objects.get(username='alice_librarian')

# Get test books
gotgame = Book.objects.get(title='A Game of Thrones')
harry = Book.objects.get(title='Harry Potter and the Philosopher\'s Stone')

print(f"\n📚 Test Data:")
print(f"  Student: {student.username}")
print(f"  Librarian: {librarian.username}")
print(f"  Book 1: {gotgame.title} (Available: {gotgame.available_copies})")
print(f"  Book 2: {harry.title} (Available: {harry.available_copies})")

# Test 1: Normal issue
print(f"\n✅ Test 1: Issue a book normally")
try:
    issue1 = issue_book_to_user(student, gotgame.id)
    print(f"   ✓ Issue created: {issue1}")
    print(f"   ✓ Due date: {issue1.due_date}")
    # Refresh from DB
    gotgame.refresh_from_db()
    print(f"   ✓ Available copies reduced: {gotgame.available_copies}")
    assert gotgame.available_copies == 2, "Available copies should be 2"
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Test 2: Normal return
print(f"\n✅ Test 2: Return a book normally (on time)")
try:
    return_book(issue1)
    print(f"   ✓ Book returned: {issue1}")
    print(f"   ✓ Penalty amount: {issue1.penalty_amount}")
    assert issue1.is_returned == True, "Should be marked as returned"
    assert issue1.penalty_amount == 0, "No penalty for on-time return"
    # Refresh from DB
    gotgame.refresh_from_db()
    print(f"   ✓ Available copies restored: {gotgame.available_copies}")
    assert gotgame.available_copies == 3, "Available copies should be 3 again"
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Test 3: Issue multiple books (up to limit of 5)
print(f"\n✅ Test 3: Issue multiple books (test 5-book limit)")
try:
    issues = []
    for i in range(5):
        book = Book.objects.filter(available_copies__gt=0).first()
        issue = issue_book_to_user(student, book.id)
        issues.append(issue)
    print(f"   ✓ Issued {len(issues)} books to student")
    
    # Try to issue 6th book (should fail)
    sixth_book = Book.objects.filter(available_copies__gt=0).first()
    if sixth_book:
        try:
            issue_book_to_user(student, sixth_book.id)
            print(f"   ✗ FAILED: Should have blocked 6th issue")
        except IssueLimitExceededException as e:
            print(f"   ✓ Correctly blocked 6th issue: {e}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Clean up active issues
BookIssue.objects.filter(user=student, is_returned=False).delete()

# Test 4: Book unavailable
print(f"\n✅ Test 4: Prevent issue when no copies available")
try:
    # Make all copies unavailable
    test_book = Book.objects.first()
    test_book.available_copies = 0
    test_book.save()
    
    try:
        issue_book_to_user(student, test_book.id)
        print(f"   ✗ FAILED: Should have blocked issue")
    except BookNotAvailableException as e:
        print(f"   ✓ Correctly blocked issue: {e}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Reset for other tests
test_book.available_copies = test_book.total_copies
test_book.save()

# Test 5: Late return with penalty
print(f"\n✅ Test 5: Late return calculates penalty correctly")
try:
    issue_late = issue_book_to_user(student, harry.id)
    
    # Simulate late return (3 days late)
    from django.utils import timezone
    late_date = issue_late.due_date + timedelta(days=3)
    late_datetime = timezone.make_aware(
        timezone.datetime.combine(late_date, timezone.datetime.min.time())
    )
    
    return_book(issue_late, return_datetime=late_datetime)
    print(f"   ✓ Late return processed")
    print(f"   ✓ Days late: 3")
    print(f"   ✓ Penalty amount: {issue_late.penalty_amount}")
    assert issue_late.penalty_amount > 0, "Should have penalty for late return"
    expected_penalty = Decimal(10) * 3  # Rate is 10 per day
    assert issue_late.penalty_amount == expected_penalty, f"Expected {expected_penalty}, got {issue_late.penalty_amount}"
    print(f"   ✓ Penalty correct: {expected_penalty}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Test 6: Cannot return already returned book
print(f"\n✅ Test 6: Cannot return already returned book")
try:
    try:
        return_book(issue_late)
        print(f"   ✗ FAILED: Should have blocked second return")
    except InvalidReturnException as e:
        print(f"   ✓ Correctly blocked re-return: {e}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Test 7: Prevent duplicate active issue
print(f"\n✅ Test 7: Prevent user from issuing same book twice (active)")
try:
    test_book = Book.objects.get(available_copies__gt=0)
    issue_dup1 = issue_book_to_user(student, test_book.id)
    
    try:
        issue_dup2 = issue_book_to_user(student, test_book.id)
        print(f"   ✗ FAILED: Should have blocked duplicate issue")
    except BookNotAvailableException as e:
        print(f"   ✓ Correctly blocked duplicate: {e}")
    finally:
        return_book(issue_dup1)
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n" + "=" * 60)
print("✅ ALL WORKFLOW TESTS COMPLETE")
print("=" * 60)
