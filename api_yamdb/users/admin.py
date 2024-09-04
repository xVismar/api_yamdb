from django.contrib import admin

from reviews.models import Category, Title, Genre, Review
from users.models import User


empty_value_display = '-пусто-'



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'year',
        'rating',
        'description'
    )
    search_fields = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'pub_date', 'score', 'text')
    search_fields = ('author', 'score',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'role',
        'email',
        'first_name',
        'last_name',
        'bio'
    )
    search_fields = ('username', 'role')