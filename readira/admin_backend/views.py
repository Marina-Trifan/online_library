from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from library.models import ReadingMaterials



class StaffRequiredMixin(UserPassesTestMixin):
    """
    Mixin that allows access only to users with staff status.

    Methods:
        test_func(): Returns True if the current user is staff.
    """
    def test_func(self):
        return self.request.user.is_staff


class BookListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    View to list all ReadingMaterials objects in the admin panel.

    Attributes:
        model (ReadingMaterials): The model to list.
        template_name (str): Template used for rendering the list.
        context_object_name (str): Name of the context variable containing the list.
    """
    model = ReadingMaterials
    template_name = 'admin_backend/book_list.html'
    context_object_name = 'books'


class BookCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """
    View to create a new ReadingMaterials object via a form.

    Attributes:
        model (ReadingMaterials): The model to create.
        template_name (str): Template used for rendering the form.
        fields (list): Fields included in the form.
        success_url (str): URL to redirect to after successful creation.
    """
    model = ReadingMaterials
    template_name = 'admin_backend/book_form.html'
    fields = ['title', 'author', 'category', 'genre', 'book_summary',
              'release_date', 'price', 'image', 'availability', 'enabled']
    success_url = reverse_lazy('admin_backend:book_list')


class BookUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """
    View to update an existing ReadingMaterials object via a form.

    Attributes:
        model (ReadingMaterials): The model to update.
        template_name (str): Template used for rendering the form.
        fields (list): Fields included in the form.
        success_url (str): URL to redirect to after successful update.
    """
    model = ReadingMaterials
    template_name = 'admin_backend/book_form.html'
    fields = ['title', 'author', 'category', 'genre', 'book_summary',
              'release_date', 'price', 'image', 'availability', 'enabled']
    success_url = reverse_lazy('admin_backend:book_list')


class BookDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """
    View to delete an existing ReadingMaterials object, with confirmation.

    Attributes:
        model (ReadingMaterials): The model to delete.
        template_name (str): Template used for rendering the confirmation page.
        success_url (str): URL to redirect to after successful deletion.
    """
    model = ReadingMaterials
    template_name = 'admin_backend/book_confirm_delete.html'
    success_url = reverse_lazy('admin_backend:book_list')