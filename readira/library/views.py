from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Author, ReadingMaterials, Review, Rating
from user_account.forms import ReviewForm
from django.utils.translation import get_language
from django.db.models import Q


# Main page view:
class MainPage(TemplateView):
    template_name = 'library/main_page.html'


# Search view:
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


# Reading Materials Views:
class ReadingMaterialsListView(ListView):
    model = ReadingMaterials
    template_name = 'reading_materials/list.html'
    context_object_name = 'materials'
    paginate_by = 20
    ordering = ['title']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['has_subscription'] = user.is_authenticated and user.has_active_subscription
        return context 

class ReadingMaterialsDetailView(DetailView):
    model = ReadingMaterials
    template_name = 'reading_materials/details.html'
    context_object_name = 'material'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        material = self.object
        context['has_subscription'] = user.is_authenticated and user.has_active_subscription

        if user.is_authenticated:
            rating = Rating.objects.filter(user=user, book=material).first()
            context['user_rating'] = rating.value if rating else 0
        else:
            context['user_rating'] = 0

        return context

    def post(self, request, *args, **kwargs):
        """Handles rating submission directly from the details page."""
        self.object = self.get_object()

        if not request.user.is_authenticated:
            return redirect('user_account:login')

        score = request.POST.get("score")
        if score and score.isdigit():
            score = int(score)
            if 1 <= score <= 5:
                # Create or update user rating
                Rating.objects.update_or_create(
                    user=request.user,
                    book=self.object,
                    defaults={"value": score}
                )

        return redirect('library:reading_material_detail', pk=self.object.pk)


# Author views:
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
   

# Review view:
class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'user_account/reviews.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.book = get_object_or_404(ReadingMaterials, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('library:reading_material_detail', kwargs = {'pk': self.kwargs['pk']})  


# Borrow View:
@login_required
def borrow_material(request, material_id):
    user = request.user
    from django.utils.timezone import now
    if not user.has_active_subscription:
        return redirect('user_account:subscriptions')
    material = get_object_or_404(ReadingMaterials, pk=material_id)
    return render(request, 'user_account/borrow_success.html', {'material': material})




