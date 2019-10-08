from django.contrib import admin

# Register your models here.
from catalog.models import Book, Author, Genre, BookInstance, Language

# admin.site.register(Book)
# admin.site.register(Author)
admin.site.register(Genre)
# admin.site.register(BookInstance)
admin.site.register(Language)


class BookInline(admin.TabularInline):
    model = Book
    extra = 0


# Define the Admin class
class AuthorAdmin(admin.ModelAdmin):
    # date_hierarchy = 'date_of_birth'
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death',)
    # search_fields = ('first_name', 'last_name')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    list_filter = ('first_name', 'last_name',)
    list_display_links = ('first_name', 'last_name',)
    inlines = [BookInline]


# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0


# Define the Book class
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre',)
    list_filter = ('genre',)
    inlines = [BooksInstanceInline]


# Define the BookInstance class
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'id',)
    list_filter = ('book', 'status', 'due_back',)
    fieldsets = (
        ('Book Information', {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )
