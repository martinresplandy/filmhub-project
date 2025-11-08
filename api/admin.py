from django.contrib import admin
from .models import Movie, Rating

# Register your models here.
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'genre', 'year']
    search_fields = ['title', 'genre']
    list_filter = ['genre', 'year']

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'score']
    list_filter = ['score']
    search_fields = ['user__username', 'movie__title']
