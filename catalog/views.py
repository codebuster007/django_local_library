import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views import generic

from catalog.forms import RenewBookForm
from catalog.models import Book, BookInstance, Author, Genre


def error_404_view(request, exception):
    data = {}
    return render(request, 'catalog/error_404.html', data)


# @login_required
def index(request):
    """View function for the home page of the site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default
    num_authors = Author.objects.count()

    # Genre that contain a particular word
    genre_instances_of_word = Genre.objects.filter(name__icontains='religion').count()

    # Book count that contain a particular word
    book_instances_of_word = Book.objects.filter(title__icontains='open').count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'genre_instances_of_word': genre_instances_of_word,
        'book_instances_of_word': book_instances_of_word,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html  with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    # login_url = '/accounts/login/'
    # redirect_field_name = 'redirect_to'
    model = Book
    context_object_name = 'book_list'  # your own name for the list as a template variable
    queryset = Book.objects.filter(title__icontains='')[:]  # Get all books containing the title war
    template_name = 'catalog/book_list'  # Specified template name/location
    paginate_by = 3

    """ Alternative way to set class based views attributes. """

    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='war')[:5]  # Get 5 books containing the title war
    #
    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get the context
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     # Create any data and add it to the context
    #     context['some_data'] = 'This is just some data'
    #     return context


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    # login_url = '/accounts/login/'
    # redirect_field_name = 'redirect_to'
    model = Book


class AuthorListView(generic.ListView):
    # login_url = '/accounts/login/'
    # redirect_field_name = 'redirect_to'
    model = Author
    context_object_name = 'author_list'
    queryset = Author.objects.all()
    template_name = 'catalog/author_list'
    paginate_by = 3


class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    # login_url = '/accounts/login/'
    # redirect_field_name = 'redirect_to'
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 2

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class AllBooksBorrowedListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 3

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(PermissionRequiredMixin, generic.CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2019'}
    permission_required = 'catalog.can_mark_returned'


class AuthorUpdate(generic.UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(generic.DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(generic.CreateView):
    model = Book
    fields = '__all__'


class BookUpdate(generic.UpdateView):
    model = Book
    fields = '__all__'


class BookDelete(generic.DeleteView):
    model = Book
    success_url = reverse_lazy('books')
