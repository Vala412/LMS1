from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from genre.models import Genre
from author.models import Author
from .models import Book
from .forms import BookModelForm

# Create your views here.

def index(req):
    """Dashboard page with statistics and recent books"""
    try:
        books = Book.objects.select_related('author').prefetch_related('genres').all()
        authors = Author.objects.all()
        genres = Genre.objects.all()

        total_books = books.count()
        total_authors = authors.count()
        total_genres = genres.count()

        recent_books = Book.objects.select_related('author').all().order_by('-created_date')[:5]

        context = {
            'books': books,
            'total_books': total_books,
            'authors': authors,
            'total_authors': total_authors,
            'total_genres': total_genres,
            'recent_books': recent_books
        }

        return render(req, 'book/index.html', context)
    except Exception as e:
        raise Http404(f"Error: {e}")

@login_required
def edit_book(request, book_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied: only staff may edit books.')
        return redirect('dashboard')
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        form = BookModelForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully.')
            return redirect('book_details', book_id=book.id)
    else:
        form = BookModelForm(instance=book)
    return render(request, 'book/edit_book.html', {'form': form, 'book': book})


@login_required
def delete_book(request, book_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied: only staff may delete books.')
        return redirect('dashboard')
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully.')
        return redirect('dashboard')
    return render(request, 'book/delete_book.html', {'book': book})

def book_details(req, book_id):
    try:
        book = Book.objects.get(pk=book_id)
    except:
        raise Http404("Book does not exist")
    
    return render(req, 'book/book_detail.html', {'book': book})


def book_page(req):
    try:
        books = Book.objects.select_related('author').prefetch_related('genres').all()

        search_book = req.GET.get('search_book', "").strip()
        if search_book:
            books = books.filter(title__icontains=search_book)

        genres = Genre.objects.all()
        selected_genre = req.GET.get('genre')

        if selected_genre:
            try:
                books = books.filter(genres__id=selected_genre)
            except ValueError:
                books = Book.objects.none()

        context = {
            'books': books,
            'genres': genres,
            'selected_genre': selected_genre,
            'search_book': search_book,
        }
        # print(context)

        return render(req, 'book/book_page.html', context)
    
    except Exception as e:
        raise Http404(f"Error: {e}")
    

def add_book(request):
    try:
        if request.method == 'POST':
            form = BookModelForm(request.POST)
            # print(form)
            if form.is_valid():
                # print(form.is_valid(), 'hello')
                form.save()
                return redirect('dashboard')
            else:
                print(form.errors)
                return render(request, 'book/add_book.html', {'add_book_form': form})
        else:
            form = BookModelForm()
            print(form.errors)
            return render(request, 'book/add_book.html', {'add_book_form': form})
    
    except Exception as e:
        raise Http404(f'Error: {e}')