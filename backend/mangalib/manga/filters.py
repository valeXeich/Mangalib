from django.db.models import Avg
from django_filters import rest_framework as filters

from .models import Manga, Genre, Tag


class MangaFilter(filters.FilterSet):
    chapters = filters.RangeFilter(field_name="chapters_count", label='Chapters count')
    release_year = filters.RangeFilter(field_name="release_year")
    rating = filters.RangeFilter(method="filter_by_rating", label="Rating")
    age_rating = filters.CharFilter(field_name="age_rating")
    genres = filters.ModelMultipleChoiceFilter(field_name="genres", queryset=Genre.objects.all())
    tags = filters.ModelMultipleChoiceFilter(field_name="tag", queryset=Tag.objects.all())
    type = filters.CharFilter(field_name="type")
    status = filters.CharFilter(field_name="status")

    def filter_by_rating(self, queryset, name, values):
        rating_from = values.start or 0
        rating_to = values.stop or 10
        queryset_with_rating = queryset.annotate(avg_rating=Avg('ratings__star')).filter(avg_rating__range=(rating_from, rating_to))
        if not rating_from:
            queryset_without_rating = queryset.filter(ratings__isnull=True)
            queryset = queryset_with_rating | queryset_without_rating
        else:
            queryset = queryset_with_rating
        return queryset.distinct()

    class Meta:
        model = Manga
        fields = ['chapters', 'release_year', 'rating', 'age_rating', 'type', 'status', 'genres']