from django.contrib import admin

from reviews.models import Category, Title, Genre, Review, Comment, User

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
        'bio',
        'is_active',
        'is_staff',
        'is_superuser'
    )
    search_fields = ('username', 'role', 'email')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        (None, {
            'fields': (
                'username',
                'password'
            )
        }),
        ('Personal info', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'bio'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Secret info', {
            'fields': ('confirmation_code',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'review',
        'author',
        'text',
        'pub_date'

    )
    search_fields = ('author', 'review')
