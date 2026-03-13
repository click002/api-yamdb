from django.contrib import admin
from .models import Review, Comment


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'score', 'author', 'title', 'pub_date')
    search_fields = ('text',)
    list_filter = ('score', 'pub_date')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'author', 'review', 'pub_date')
    search_fields = ('text',)
    list_filter = ('pub_date',)
