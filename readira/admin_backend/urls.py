from django.urls import path
from .views import (
    BookListView,
    BookCreateView,
    BookUpdateView, 
    BookDeleteView
    )


app_name = 'admin_backend'


urlpatterns = [
    path('books/', BookListView.as_view(), name='book_list'),
    path('books/create/', BookCreateView.as_view(), name='book_create'),
    path('books/<int:pk>/edit/', BookUpdateView.as_view(), name='book_edit'),
    path('books/<int:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),
]