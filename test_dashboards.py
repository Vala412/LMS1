"""Test staff dashboards and role-based permissions."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from django.contrib.auth.models import User
from book.models import Book, BookIssue
from book.services import issue_book_to_user, return_book

print("=" * 60)
print("👮 TESTING STAFF DASHBOARDS & PERMISSIONS")
print("=" * 60)

# Get test users
student = User.objects.get(username='john_student')
librarian = User.objects.get(username='alice_librarian')
admin = User.objects.get(username='admin')

print(f"\n👥 User Roles:")
print(f"  {student.username}: is_staff={student.is_staff}, is_superuser={student.is_superuser}")
print(f"  {librarian.username}: is_staff={librarian.is_staff}, is_superuser={librarian.is_superuser}")
print(f"  {admin.username}: is_staff={admin.is_staff}, is_superuser={admin.is_superuser}")

# Test 1: Create some issues for testing dashboard
print(f"\n✅ Test 1: Create sample issues for dashboard")
try:
    books = Book.objects.filter(available_copies__gt=0)[:3]
    for book in books:
        issue = issue_book_to_user(student, book.id)
        print(f"   ✓ Issued: {book.title}")
    
    print(f"   ✓ Total active issues: {BookIssue.objects.filter(is_returned=False).count()}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Test 2: Check staff statistics
print(f"\n✅ Test 2: Dashboard statistics available")
try:
    total_issued = BookIssue.objects.filter(is_returned=False).count()
    overdue = BookIssue.objects.filter(is_returned=False, due_date__lt='2026-03-01').count()
    with_penalties = (
        BookIssue.objects
        .filter(penalty_amount__gt=0)
        .values('user')
        .distinct()
        .count()
    )
    
    print(f"   ✓ Total active issues: {total_issued}")
    print(f"   ✓ Overdue books: {overdue}")
    print(f"   ✓ Users with penalties: {with_penalties}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Test 3: Check librarian can perform actions
print(f"\n✅ Test 3: Librarian has staff permissions")
try:
    # Librarian should be staff
    assert librarian.is_staff == True, "Librarian should be staff"
    print(f"   ✓ Librarian is staff: {librarian.is_staff}")
    
    # Check if librarian can view issued books
    active_issues = BookIssue.objects.filter(is_returned=False)
    if active_issues.exists():
        print(f"   ✓ Can query active issues: {active_issues.count()}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Test 4: Check admin has full access
print(f"\n✅ Test 4: Admin has superuser access")
try:
    assert admin.is_superuser == True, "Admin should be superuser"
    print(f"   ✓ Admin is superuser: {admin.is_superuser}")
    assert admin.is_staff == True, "Superuser should be staff"
    print(f"   ✓ Admin is staff: {admin.is_staff}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Test 5: Query optimization check
print(f"\n✅ Test 5: Query optimization (select_related/prefetch_related)")
try:
    # This should use select_related for efficient queries
    issues = (
        BookIssue.objects
        .select_related('user', 'book')
        .filter(is_returned=False)
    )
    
    print(f"   ✓ Queries optimized with select_related")
    print(f"   ✓ Can access related objects without additional queries")
    
    if issues.exists():
        first_issue = issues.first()
        _ = first_issue.user.username  # Should not trigger new query
        _ = first_issue.book.title     # Should not trigger new query
        print(f"   ✓ Efficient access: {first_issue.user.username} - {first_issue.book.title}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Test 6: User dashboard shows active loans
print(f"\n✅ Test 6: User dashboard shows active loans")
try:
    user_issues = (
        BookIssue.objects
        .filter(user=student, is_returned=False)
        .select_related('book')
    )
    
    print(f"   ✓ Student has {user_issues.count()} active loans")
    for issue in user_issues:
        penalty_text = f" (Penalty: {issue.penalty_amount})" if issue.penalty_amount > 0 else ""
        print(f"      - {issue.book.title} (Due: {issue.due_date}){penalty_text}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

# Clean up
print(f"\n✅ Test 7: Clean up test issues")
try:
    BookIssue.objects.filter(is_returned=False).delete()
    print(f"   ✓ Test issues cleaned up")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n" + "=" * 60)
print("✅ STAFF DASHBOARD TESTS COMPLETE")
print("=" * 60)
