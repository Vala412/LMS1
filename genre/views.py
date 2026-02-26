from django.shortcuts import render
from .models import Genre
from book.models import Book
from django.db.models import Count
from django.core.exceptions import ValidationError
from django.http import Http404

def genre_search(req):
    try:
        # Fetch all genres and count books in one query for efficiency
        genres = Genre.objects.annotate(num_books=Count('books'))
        
        # Start with all books
        books = Book.objects.all()

        # Get the genre ID from the search query
        search_query = req.GET.get('search_query')

        if search_query:
            try:
                books = books.filter(genres__id=search_query)
            except (ValueError, ValidationError):
                books = Book.objects.none()

        context = {
            'genres': genres,
            'books': books,
            'search_query': search_query,
        }
        return render(req, 'genre/genre_search.html', context)

    except Exception as e:
        raise Http404(f"Error: {e}")