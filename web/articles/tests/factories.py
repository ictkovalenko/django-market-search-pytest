import factory.faker
from django.utils.text import slugify

from web.articles.models import Article, Category


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    title = factory.Faker('word')
    slug = factory.LazyAttribute(lambda x: slugify(x.title))


class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article

    title = factory.Faker('name')
    slug = factory.LazyAttribute(lambda x: slugify(x.title))
    text = factory.Faker('word')
