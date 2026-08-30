from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Tag, Article
from .serializers import CategorySerializer, TagSerializer, ArticleListSerializer, ArticleDetailSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'
    pagination_class = None


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.filter(is_published=True).select_related('category').prefetch_related('tags')
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'tags__slug']
    search_fields = ['title', 'excerpt', 'body']
    ordering_fields = ['published_at', 'title']
    ordering = ['-published_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer
