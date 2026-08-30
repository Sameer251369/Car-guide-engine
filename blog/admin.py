from django.contrib import admin
from .models import Category, Tag, Article

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author_name', 'published_at', 'is_published')
    list_filter = ('category', 'is_published', 'tags')
    search_fields = ('title', 'excerpt', 'body')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
