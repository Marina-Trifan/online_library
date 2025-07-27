from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Author, ReadingMaterials, Review, Rating
from user_account.forms import ReviewForm, RatingForm
from django.utils.translation import get_language
from django.db.models import Q



class MainPage(TemplateView):
    template_name = 'library/main_page.html'

def search_view(request):
    query = request.GET.get('q', '')
    results_books = []
    results_authors = []

    if query:
        results_books = ReadingMaterials.objects.filter(title__icontains=query)
        results_authors = Author.objects.filter(name__icontains=query) | Author.objects.filter(surname__icontains=query)

    return render(request, "library/search.html", {
        "query": query,
        "results_books": results_books,
        "results_authors": results_authors,
        "LANGUAGE_CODE": get_language()
    })

# Reading Materials View

class ReadingMaterialsListView(ListView):
    model = ReadingMaterials
    template_name = 'reading_materials/list.html'
    context_object_name = 'materials'
    paginate_by = 20
    ordering = ['title'] 


class ReadingMaterialsDetailView(DetailView):
    model=ReadingMaterials
    template_name = 'reading_materials/details.html'
    context_object_name = 'material'

# Author View

class AuthorListView(ListView):
    model = Author
    template_name = 'authors/list.html'
    context_object_name = 'authors'
    paginate_by = 20
    ordering = ['name']

class AuthorDetailView(LoginRequiredMixin, DetailView):
    model = Author
    template_name = 'authors/details.html'
    context_object_name = 'author'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('user_account:login')
        return super().dispatch(request, *args, **kwargs)
   

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




