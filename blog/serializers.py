from rest_framework import serializers
from .models import Category, Tag, Article

class CategorySerializer(serializers.ModelSerializer):
    article_count = serializers.IntegerField(source='articles.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'article_count']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class ArticleListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'category_name', 'category_slug',
            'tags', 'featured_image_url', 'excerpt', 'author_name',
            'published_at', 'is_published'
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'category', 'tags',
            'featured_image_url', 'excerpt', 'body', 'author_name',
            'published_at', 'is_published', 'meta_title', 'meta_description'
        ]
