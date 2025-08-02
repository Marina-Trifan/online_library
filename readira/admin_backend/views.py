from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from library.models import ReadingMaterials



# Staff view: allows access only to users with staff role
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

# Reading Materials list view: used for listing all materials in the admin panel
class BookListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = ReadingMaterials
    template_name = 'admin_backend/book_list.html'
    context_object_name = 'books'

# Reading Materials create view: used for adding a new material - add form
class BookCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = ReadingMaterials
    template_name = 'admin_backend/book_form.html'
    fields = ['title', 'author', 'category', 'genre', 'book_summary',
              'release_date', 'price', 'image', 'availability', 'enabled']
    success_url = reverse_lazy('admin_backend:book_list')

# Reading Materials update view: used for updating an existing material - update form
class BookUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = ReadingMaterials
    template_name = 'admin_backend/book_form.html'
    fields = ['title', 'author', 'category', 'genre', 'book_summary',
              'release_date', 'price', 'image', 'availability', 'enabled']
    success_url = reverse_lazy('admin_backend:book_list')

# Reading Materials delete view: used for deleting a material - confirm before deletion
class BookDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = ReadingMaterials
    template_name = 'admin_backend/book_confirm_delete.html'
    success_url = reverse_lazy('admin_backend:book_list')