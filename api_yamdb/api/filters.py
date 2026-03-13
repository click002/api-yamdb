from django_filters import rest_framework as df_filters
from reviews.models import Title


class TitleFilter(df_filters.FilterSet):
    """Фильтр для произведений по genre, category, year, name."""
    genre = df_filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='exact'
    )
    category = df_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact'
    )
    year = df_filters.NumberFilter(
        field_name='year',
        lookup_expr='exact'
    )
    name = df_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Title
        fields = ['genre', 'category', 'year', 'name']
