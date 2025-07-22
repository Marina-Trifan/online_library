from django.urls import path
from .views import (
    MainPage,
    AuthorListView,
    AuthorDetailView,
    ReadingMaterialsListView,
    ReadingMaterialsDetailView,
    ReviewCreateView,
    RatingCreateView,
    GenreListView,
    GenreDetailView,
    author_access_denied)

app_name='library'

urlpatterns = [
    path('materials/', ReadingMaterialsListView.as_view(), name='reading_materials'),
    path('materials/<int:pk>/', ReadingMaterialsDetailView.as_view(), name='reading_material_detail'),
    path('authors/', AuthorListView.as_view(), name='author_list'),
    path('author/<int:pk>/', AuthorDetailView.as_view(), name='author_details'),
    path('author/access-denied/', author_access_denied, name='author_access_denied'),
    path('genres/', GenreListView.as_view(), name='genre_list'),
    path('genres/<int:pk>/', GenreDetailView.as_view(), name = 'genre_details'),
    path('materials/<int:pk>/review/', ReviewCreateView.as_view(), name='create_review'),
    path('materials/<int:pk>/rating', RatingCreateView.as_view(), name='create_rating'),
]