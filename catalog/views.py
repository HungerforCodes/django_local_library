import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from catalog.forms import RenewBookForm

# Create your views here.

def index(request):
    """view function for home page of site"""
    
    # Generate counts of some of the main object
    num_books = Book.objects.all().count()
    num_instance = BookInstance.objects.all().count()
    
    # available books (status = 'a')
    num_instance_available = BookInstance.objects.filter(status__exact='a').count()
    
    # the 'all()' is implied by default
    num_authors = Author.objects.count()
    
    # number of visits
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    
    context = {
        'num_books': num_books,
        'num_instance': num_instance,
        'num_instance_available': num_instance_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }
    
    # render the html template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 2 

class BookDetailView(generic.DetailView):
    model = Book
    
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    
    if request.method == 'POST':
        form = RenewBookForm(request.POST)
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()
            return HttpResponseRedirect(reverse('all-borrowed'))
        else:
            proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
            form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
        
        context = {
            'form': form,
            'book_instance': book_instance,
        }
        
        return render(request, 'catalog/book_renew_librarian.html', context)