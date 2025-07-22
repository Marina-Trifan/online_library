from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Author, ReadingMaterials, Review, Rating, Genre
from user_account.forms import ReviewForm, RatingForm

class MainPage(TemplateView):
    template_name = 'library/main_page.html'


# Reading Materials View

class ReadingMaterialsListView(ListView):
    model = ReadingMaterials
    template_name = 'reading_materials/list.html'
    context_object_name = 'materials'


class ReadingMaterialsDetailView(DetailView):
    model=ReadingMaterials
    template_name = 'reading_materials/details.html'
    context_object_name = 'material'

# Author View

class AuthorListView(ListView):
    model = Author
    template_name = 'authors/list.html'
    context_object_name = 'authors'

class AuthorDetailView(LoginRequiredMixin, DetailView):
    model = Author
    template_name = 'authors/details.html'
    context_object_name = 'author'
    login_url = reverse_lazy('author_access_denied')
    redirect_field_name = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('author_access_denied')
        return super().dispatch(request, *args, **kwargs)

def author_access_denied(request):
    return render(request, 'authors/access_denied.html')

# Genre View
class GenreListView(ListView):
    model = Genre
    template_name = 'genres/list.html'
    context_object_name = 'genres'

class GenreDetailView(DetailView):
    model = Genre
    template_name = 'genre/details.html'
    context_object_name = 'genre'    

# Review View

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.book = get_object_or_404(ReadingMaterials, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('library:reading_material_detail', kwargs = {'pk': self.kwargs['pk']})


# Rating View

class RatingCreateView(LoginRequiredMixin, CreateView):
    model = Rating
    form_class = RatingForm
    template_name = 'rating/form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.book = get_object_or_404(ReadingMaterials, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('library:reading_material_detail', kwargs={'pk': self.kwargs['pk']})
