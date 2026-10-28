from django.contrib import admin

from articles.models import Article, Catalog

admin.site.register(Article)
admin.site.register(Catalog)
