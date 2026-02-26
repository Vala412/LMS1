from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Author, Profile
from book.models import Book

# Create your views here.

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


def author_details(req, author_id):
    try:
        author = Author.objects.select_related('profile').prefetch_related('books').get(pk=author_id)
    except Author.DoesNotExist:
        raise Http404('Author does not exist')

    return render(req, 'author/author_detail.html', {'author': author})


def profile_details(req, profile_id):
    try:
        profile = Profile.objects.select_related('user', 'author').get(pk=profile_id)
    except Profile.DoesNotExist:
        raise Http404('Profile does not exist')

    return render(req, 'author/profile_detail.html', {'profile': profile})


def author_view(req):
    try:
        author_name = req.GET.get("author", "").strip()
        pub_year = req.GET.get("year", "")
        book_name = req.GET.get("book_name", "").strip()

        books = Book.objects.select_related('author').all()

        if author_name:
            books = books.filter(author__name__icontains=author_name)

        if pub_year and pub_year.isdigit():
            books = books.filter(published_date__year__gte=int(pub_year))

        if book_name:
            books = books.filter(title__icontains=book_name)

        # get authors from filtered books - optimized query
        authors = Author.objects.filter(books__in=books).prefetch_related('books').distinct()

        context = {
            'authors': authors,
            'books': books,  
            'author_name': author_name,
            'year': pub_year,
            'book_name': book_name
        }
    except Exception as e:
        raise Http404(f"Error: {e}")

    return render(req, 'author/author_view.html', context)

@login_required
def user_profile_view(request):
    """User-specific profile page"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Get associated author if exists
    author = None
    try:
        author = request.user.profile.author
    except (Profile.DoesNotExist, AttributeError):
        pass
    
    user_books = []
    if author:
        user_books = author.books.select_related('author').prefetch_related('genres').all()
    
    context = {
        'profile': profile,
        'author': author,
        'user_books': user_books,
    }
    return render(request, 'author/user_profile.html', context)
