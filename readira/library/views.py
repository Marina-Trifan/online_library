from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import get_language
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from user_account.forms import ReviewForm
from .models import Author, ReadingMaterials, Review, Rating



class MainPage(TemplateView):
    """
    Represents the main landing page of the library.
    Methods:
        get_context_data(): Retrieves context for rendering the main page.
    """
    template_name = 'library/main_page.html'


class ReadingMaterialsListView(ListView):
    """
    Displays a paginated list of reading materials such as books, articles, etc.
    Attributes:
        model (class): The model to be used for fetching objects (ReadingMaterials).
        template_name (str): The template for rendering the list.
        context_object_name (str): The context name used to access the list in the template.
        paginate_by (int): Number of items to display per page.
        ordering (list): The ordering of the results (based on title).
    Methods:
        get_context_data(): Adds additional context to the reading materials list view, such as the user's subscription status.
                            Args:
                                **kwargs: Arbitrary keyword arguments passed to the method.
                            Returns:
                                dict: Context data for rendering the template.
    """
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
    """
    Displays detailed information about a specific reading material. 
    Allows users to submit ratings for the material.
    Attributes:
        model (class): The model to be used for fetching the object (ReadingMaterials).
        template_name (str): The template for rendering the material details.
        context_object_name (str): The context name used to access the material in the template.
    Methods:
        get_context_data(): Adds additional context to the material detail view, such as user ratings and subscription status.
                            Args:
                                **kwargs: Arbitrary keyword arguments passed to the method.
                            Returns:
                                dict: Context data for rendering the template.
        post(): Handles rating submissions directly from the details page.
                Args:
                    request: The HTTP request object containing the rating data.
                Returns:
                    Redirect to the same material's detail page after saving the rating.
    """
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
        self.object = self.get_object()

        if not request.user.is_authenticated:
            return redirect('user_account:login')

        score = request.POST.get('score')
        if score and score.isdigit():
            score = int(score)
            if 1 <= score <= 5:
                # Create or update user rating
                Rating.objects.update_or_create(
                    user=request.user,
                    book=self.object,
                    defaults={'value': score}
                )

        return redirect('library:reading_material_detail', pk=self.object.pk)



class AuthorListView(ListView):
    """
    Displays a paginated list of authors in the library database.
    Attributes:
        model (class): The model to be used for fetching objects (Author).
        template_name (str): The template for rendering the author list.
        context_object_name (str): The context name used to access the list of authors in the template.
        paginate_by (int): Number of items to display per page.
        ordering (list): The ordering of the results (based on author's name).
    """
    model = Author
    template_name = 'authors/list.html'
    context_object_name = 'authors'
    paginate_by = 20
    ordering = ['name']


class AuthorDetailView(LoginRequiredMixin, DetailView):
    """
    Displays detailed information about a specific author, including their works
    Attributes:
        model (class): The model to be used for fetching the object (Author).
        template_name (str): The template for rendering the author detail.
        context_object_name (str): The context name used to access the author in the template.
    Methods:
        dispatch(): Redirects unauthenticated users to the login page.
                    Args:
                        request: The HTTP request object.
                        *args: Variable-length arguments.
                        **kwargs: Arbitrary keyword arguments.
                    Returns:
                        HttpResponseRedirect: A redirect to the login page if not authenticated.
    """
    model = Author
    template_name = 'authors/details.html'
    context_object_name = 'author'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('user_account:login')
        return super().dispatch(request, *args, **kwargs)
   


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """
    Allows authenticated users to create a review for a specific reading material.
    Attributes:
        model (class): The model to be used for creating the review (Review).
        form_class (class): The form class to be used for review submission.
        template_name (str): The template for rendering the review form.
    Methods:
        form_valid(): Sets the user and book for the review before saving.
                    Args:
                        form: The review form instance.
                    Returns:
                        Form instance with the updated user and book information.
        get_success_url(): Redirects to the material detail page after review submission.
                        Returns:
                            str: The URL to redirect to (reading material detail page).
    """
    model = Review
    form_class = ReviewForm
    template_name = 'user_account/reviews.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.book = get_object_or_404(ReadingMaterials, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('library:reading_material_detail', kwargs = {'pk': self.kwargs['pk']})  


def search_view(request):
    """
    Handles the search functionality for books and authors. 
    Args:
        request: The HTTP request object containing the search query.
    Returns:
        Rendered search results page with books and authors based on the query.
    """
    query = request.GET.get('q', '')
    results_books = []
    results_authors = []

    if query:
        results_books = ReadingMaterials.objects.filter(title__icontains=query)
        results_authors = Author.objects.filter(name__icontains=query) | Author.objects.filter(surname__icontains=query)

    return render(request, 'library/search.html', {
        'query': query,
        'results_books': results_books,
        'results_authors': results_authors,
        'LANGUAGE_CODE': get_language()
    })


@login_required
def borrow_material(request, material_id):
    """
    Allows a user to borrow a specific reading material, provided they have an active subscription.
    Args:
        request: The HTTP request object.
        material_id (int): The ID of the reading material to be borrowed.
    Returns:
        Rendered borrow success page if the user has an active subscription, else redirects to the subscriptions page.
    """
    user = request.user
    from django.utils.timezone import now
    if not user.has_active_subscription:
        return redirect('user_account:subscriptions')
    material = get_object_or_404(ReadingMaterials, pk=material_id)
    return render(request, 'user_account/borrow_success.html', {'material': material})




