from django.contrib import admin

from .models import Manga, Genre, Author, Publisher, Painter, Volume, Chapter, Page, Rating, Comment, RatingComment


@admin.register(Manga)
class MangaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Genre)
admin.site.register(Author)
admin.site.register(Painter)
admin.site.register(Publisher)
admin.site.register(Volume)
admin.site.register(Page)
admin.site.register(Rating)
admin.site.register(Comment)
admin.site.register(RatingComment)


