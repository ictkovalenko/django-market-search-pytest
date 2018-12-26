import html

from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from rest_framework import status

from web.articles.models import Article
from web.system.models import PermanentlyRemoved


class ArticleDetailView(DetailView):
    template_name = 'pages/articles/article.html'
    context_object_name = 'article'

    def dispatch(self, request, *args, **kwargs):
        removed_item = PermanentlyRemoved.objects.filter(
            url=request.path, status=status.HTTP_301_MOVED_PERMANENTLY).first()
        if removed_item:
            return HttpResponsePermanentRedirect(removed_item.redirect_url)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Article, slug=self.kwargs['article_slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = html.unescape(self.object.text)
        return context
