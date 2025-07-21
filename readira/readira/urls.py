"""
URL configuration for readira project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import set_language
from library.views import MainPage, AuthorListView, AuthorDetailView, ReadingMaterialsListView, ReadingMaterialsDetailView, ReviewCreateView, RatingCreateView, GenreListView, GenreDetailView
from user_account.views import CustomLoginView, RegisterView, logout_view
from django.contrib.auth.views import LogoutView
from django.contrib.auth import logout


urlpatterns = [
    path('set_language/', set_language, name = 'set_language'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns +=i18n_patterns (
    path('admin/', admin.site.urls),
    path('', MainPage.as_view(), name='main_page'),
    path('materias/', ReadingMaterialsListView.as_view(), name='reading_materials'),
    path('materials/<int:pk>/', ReadingMaterialsDetailView.as_view(), name='reading_material_detail'),
    path('authors/', AuthorListView.as_view(), name='author_list'),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author_details'),
    path('genres/', GenreListView.as_view(), name='genre_list'),
    path('genres/<int:pk>/', GenreDetailView.as_view(), name = 'genre_details'),
    path('materials/<int:pk>/review/', ReviewCreateView.as_view(), name='create_view'),
    path('materials/<int:pk>/rating', RatingCreateView.as_view(), name='create_rating'),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
