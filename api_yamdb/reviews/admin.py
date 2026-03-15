from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Category, Comment, Genre, Review, Title, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'bio', 'confirmation_code')
    list_filter = ('role',)
    search_fields = ('username', 'email')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category', 'genre_list')
    list_filter = ('year', 'category')
    filter_horizontal = ('genre',)

    def genre_list(self, obj):
        return ', '.join([g.name for g in obj.genre.all()])
    genre_list.short_description = 'Жанры'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'score', 'pub_date', 'short_review')
    list_filter = ('score', 'pub_date')

    def short_review(self, obj):
        if len(obj.text) > 50:
            return obj.text[:50] + '...'
        return obj.text
    short_review.short_description = 'Отзыв'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('review', 'author', 'pub_date', 'short_comment')

    def short_comment(self, obj):
        if len(obj.text) > 50:
            return obj.text[:50] + '...'
        return obj.text
    short_comment.short_description = 'Комментарий'
