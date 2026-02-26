from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.index, name='dashboard'),
    path('', views.index, name='home'),
    path('book/<int:book_id>', views.book_details, name='book_details'),
    path('book/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('book/<int:book_id>/delete/', views.delete_book, name='delete_book'),
    path('book_page/', views.book_page, name='book_page'),
    path('add_book/', views.add_book, name='add_book'),
]
