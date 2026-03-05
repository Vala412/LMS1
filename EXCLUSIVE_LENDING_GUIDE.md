# 🔒 Exclusive Single-Copy Lending System

## Overview

Your Django library system now supports **exclusive single-copy lending**. When a book is set as a single-copy book, only **one user can hold it at a time**. Other users are automatically blocked from issuing it until the current holder returns it.

This feature is **already built-in** and works automatically based on the `total_copies` value set for each book.

---

## How It Works

### How the System Decides
The system checks the **`total_copies`** field for each book:

```
IF total_copies = 1:
  ✓ SINGLE-COPY MODE (Exclusive Lending)
  ✓ Only 1 user can hold it at a time
  ✓ Others are BLOCKED with "no copies available" message

IF total_copies > 1:
  ✓ MULTI-COPY MODE (Regular Library)
  ✓ Multiple users can hold different copies simultaneously
  ✓ Each user can get a copy until all are issued
```

### Key Fields

| Field | Purpose |
|-------|---------|
| `total_copies` | Total physical copies in library (set this!) |
| `available_copies` | How many copies are currently NOT issued |
| `is_returned` (BookIssue) | Whether a loan is active or completed |

---

## Exclusive Lending Flow

### Scenario 1: Single-Copy Book

```
Book: "The Great Gatsby" 
total_copies = 1, available_copies = 1

Step 1: John issues it
  ✓ John gets the book
  ✓ available_copies becomes 0
  
Step 2: Jane tries to issue it
  ✗ BLOCKED: "The Great Gatsby has no copies available"
  ✓ Only John has exclusive access
  
Step 3: John returns it
  ✓ John returns to library
  ✓ available_copies back to 1
  
Step 4: Jane can now issue it
  ✓ Jane can finally get the book
  ✓ Now ONLY Jane has exclusive access
```

### Scenario 2: Multi-Copy Book

```
Book: "Harry Potter" 
total_copies = 3, available_copies = 3

Step 1: John issues it
  ✓ John gets copy 1
  ✓ available_copies becomes 2
  
Step 2: Jane issues it
  ✓ Jane gets copy 2
  ✓ available_copies becomes 1
  
Step 3: Bob issues it
  ✓ Bob gets copy 3
  ✓ available_copies becomes 0
  
Step 4: Sarah tries to issue it
  ✗ BLOCKED: "Harry Potter has no copies available"
  ✓ Wait for someone to return one
```

---

## Managing Single vs Multi-Copy Books

### 1. **Via Django Admin** (Easiest)

1. Go to `http://localhost:8000/admin/`
2. Click "Books" → Select a book
3. You'll see:
   - **Copy Status**: Shows "🔒 Single-Copy" or "📚 Multi-Copy (N copies)"
   - **Availability**: Shows current status
   - **Inventory & Copies** section:
     - `total_copies`: Change this value
     - `available_copies`: Auto-resets when you save

#### Example: Convert a book to single-copy

```
BEFORE:
  total_copies = 5
  available_copies = 3

ACTION:
  Change total_copies to 1
  Click Save

AFTER:
  total_copies = 1
  available_copies = 1  (auto-reset)
  Status: 🔒 Single-Copy
```

### 2. **Via Management Command** (For Bulk Operations)

```bash
# Set a specific book to single-copy
python manage.py configure_book_copies <BOOK_ID> --single

# Set a specific book to have N copies
python manage.py configure_book_copies <BOOK_ID> --multi 5

# Example:
python manage.py configure_book_copies 1 --single
# Output: ✓ 'The Hobbit' updated: Total copies: 3 → 1
```

### 3. **Via Django Shell** (For Scripting)

```python
python manage.py shell

from book.models import Book

# Convert to single-copy
book = Book.objects.get(id=1)
book.total_copies = 1
book.available_copies = 1
book.save()

# Verify
print(f"Is single-copy: {book.total_copies == 1}")
print(f"Available: {book.available_copies}")
```

---

## Admin Interface Features

The enhanced Book admin now shows:

### List View Columns
- **Copy Status**: Visual badge showing single vs multi-copy
- **Availability**: Color-coded status
  - 🟢 Green = All Available
  - 🟡 Orange = Partially Available
  - 🔴 Red = All Issued

### Detail View
- **Inventory & Copies** section with detailed information box
- **Availability Info**: Shows:
  - Copy type (Single vs Multi)
  - Current status
  - How many issued vs available
  - Clear warnings for exclusive lending mode

### Example Admin Screen

```
Book Title: The Hobbit
Copy Status: 🔒 Single-Copy
Availability: ❌ All Issued (0/1)

Inventory & Copies Section:
  ├ Copy Type: Single-Copy (Exclusive Lending)
  ├ Status: ❌ ALL COPIES CURRENTLY ISSUED - NOT AVAILABLE
  ├ Issued: 1 / 1
  └ Available for Users: 0
```

---

## Code Behind the Magic

The exclusive lending works through these components:

### 1. **BookIssue Model** (Tracks loans)
```python
class BookIssue(models.Model):
    user = ForeignKey(User)
    book = ForeignKey(Book)
    issued_at = DateTimeField(auto_now_add=True)
    returned_at = DateTimeField(null=True)
    is_returned = BooleanField(default=False)
```

### 2. **Issue Logic** (`book/services.py`)
```python
def issue_book_to_user(user, book_id):
    book = Book.objects.get(id=book_id)
    
    # Check 1: Is copy available?
    if book.available_copies <= 0:
        raise BookNotAvailableException(f"{book.title} has no copies available")
    
    # Check 2: Active issue limit
    if user.bookissue_set.filter(is_returned=False).count() >= 5:
        raise IssueLimitExceededException("Max 5 books at a time")
    
    # Check 3: Prevent duplicates (user can't have 2 active loans of same book)
    if BookIssue.objects.filter(user=user, book=book, is_returned=False).exists():
        raise BookAlreadyIssuedException("You already have this book")
    
    # Issue the book (atomic update)
    book.available_copies -= 1  # Actually uses F() for atomicity
    book.save()
    
    # Create issue record
    return BookIssue.objects.create(user=user, book=book)
```

### 3. **Return Logic** 
```python
def return_book(issue):
    issue.is_returned = True
    issue.returned_at = now()
    issue.save()
    
    # Restore available copies (atomic)
    book.available_copies += 1
    book.save()
```

### 4. **Exclusive Enforcement**
- When `total_copies = 1`, the available becomes 0 immediately after issue
- This blocks all other users automatically
- No special code needed—it's the natural behavior of the inventory system

---

## Real-World Examples

### Example 1: Rare Book (Single Copy)

```
"First Edition Harry Potter" 
total_copies = 1 (only one physical copy exists!)

Behavior:
  Day 1: Student A issues → Available: 0/1 (A has exclusive access)
  Day 2: Student B tries → BLOCKED ❌ 
  Day 7: A returns it
  Day 8: Student C issues → Available: 0/1 (C has exclusive access)
```

### Example 2: Popular Book (5 Copies)

```
"Harry Potter" 
total_copies = 5

Behavior:
  Day 1: John issues → Available: 4/5
  Day 1: Jane issues → Available: 3/5
  Day 1: Bob issues → Available: 2/5
  Day 2: Sarah issues → Available: 1/5
  Day 2: Mike issues → Available: 0/5
  Day 3: Paul tries → BLOCKED (0 available, but not due to John/Jane—one of the 5)
```

### Example 3: Textbook (20 Copies)

```
"Chemistry 101" (Course required)
total_copies = 20

Can support:
  ✓ 20 students simultaneously
  ✓ Most students never wait
  ✓ Popular book always has copies available
```

---

## Testing

Run the comprehensive test suite to see exclusive lending in action:

```bash
python test_single_copy.py
```

**Output includes:**
- ✅ First user issues single-copy book
- ✅ Second user blocked
- ✅ First user returns, book available again
- ✅ Second user can now issue
- ✅ Multi-copy books allow concurrent access
- ✅ Detailed insights on the system

---

## Troubleshooting

### Issue: "This book has no copies available"

**Cause**: All copies are checked out  
**Solution**:
1. Check admin how many copies total: `total_copies`
2. See how many are issued (issued ones marked `is_returned=False`)
3. For single-copy books: Wait for current user to return it
4. For multi-copy books: Wait for any user to return a copy

### Issue: "'The Great Gatsby' in admin shows all issued"

**Check**:
1. Click the book in admin
2. Look at **Availability Info** section
3. See how many issued vs total
4. For urgent access: Admin can manually mark as `is_returned=True` in BookIssue

### Issue: Want to change from multi-copy to single-copy

**Steps**:
1. Go to admin
2. Click the book
3. Change `total_copies` from N to 1
4. Click Save
5. `available_copies` auto-resets to 1
6. Any new issues blocked if copies issued

---

## Best Practices

### ✅ DO

- Set `total_copies=1` for valuable/rare books
- Use multi-copy for popular/required texts
- Regularly review admin to see what's checked out
- Update copy counts when you physically add books
- Use the management command for bulk updates

### ❌ DON'T

- Manually edit `available_copies` (it auto-updates on issue/return)
- Set `total_copies=0` (books disappear from system)
- Delete books with active loans (mark returns first)
- Issue to the same user twice (system prevents this)

---

## Summary

| Feature | Your System |
|---------|-----------|
| **Single-Copy Exclusive Lending** | ✅ Built-in & Auto |
| **Block other users** | ✅ Automatic |
| **Multi-Copy Support** | ✅ Yes |
| **Concurrent Access** | ✅ Works great |
| **Easy Configuration** | ✅ Admin UI or command |
| **Permanent Exclusivity** | ✅ Until returned |
| **No Override Needed** | ✅ Just return book |

Your system is ready to go! 🎉
