from django.contrib import admin

from web.articles.models import Article, Category


class ArticleAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_filter = ('category',)
    list_display = ('short_title', 'article_url', 'featured', 'published_date', 'category')

    def article_url(self, obj):
        url = obj.get_absolute_url()
        return '<a target="_blank" href="%s">%s</a>' % (url, url)

    article_url.allow_tags = True


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')


admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
