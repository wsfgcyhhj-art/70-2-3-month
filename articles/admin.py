from django.contrib import admin

from articles.models import Article, Catalog, Comment

admin.site.register(Article)
admin.site.register(Catalog)
admin.site.register(Comment)
