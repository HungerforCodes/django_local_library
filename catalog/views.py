from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic

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