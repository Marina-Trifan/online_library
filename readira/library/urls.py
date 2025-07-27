from django.urls import path
from .views import (
    MainPage,
    AuthorListView,
    AuthorDetailView,
    ReadingMaterialsListView,
    ReadingMaterialsDetailView,
    ReviewCreateView,
    RatingCreateView,
    borrow_material,
    )

app_name='library'

urlpatterns = [
    path('materials/', ReadingMaterialsListView.as_view(), name='reading_materials'),
    path('materials/<int:pk>/', ReadingMaterialsDetailView.as_view(), name='reading_material_detail'),
    path('authors/', AuthorListView.as_view(), name='author_list'),
    path('author/<int:pk>/', AuthorDetailView.as_view(), name='author_details'),
    path('materials/<int:pk>/review/', ReviewCreateView.as_view(), name='create_review'),
    path('materials/<int:pk>/rating', RatingCreateView.as_view(), name='create_rating'),
    path('materials/<int:material_id>/borrow/', borrow_material, name='borrow_material')
]