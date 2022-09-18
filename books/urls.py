from django.urls import path
from .views import HelloAPI, bookAPI, booksAPI, BookAPI, BooksAPI,BooksAPIMixins

urlpatterns = [
    path('hello/', HelloAPI),
    path('fbv/books/', booksAPI),
    path('fbv/book/<int:bid>/', bookAPI),
    path('cbv/books/', BooksAPI.as_view()),
    path('cbv/book/<int:bid>/', BookAPI.as_view()),

    path('mixin/books/', BooksAPIMixins.as_view()),
    path('mixin/book/<int:bid>/', BooksAPIMixins.as_view()),
]