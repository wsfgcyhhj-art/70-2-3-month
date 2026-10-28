from django.http.request import HttpRequest
from django.http.response import HttpResponse

from articles.models import Article, Catalog


def articles_list(request: HttpRequest) -> HttpResponse:
    count: int = Article.objects.all().count()
    text = "<h1>"
    for i in range(1, count + 1):
        article = Article.objects.filter(id=i).first()
        text += f"{article.title} </h1><br><h1>"
    return HttpResponse(text)


def catalog_list(request: HttpRequest) -> HttpResponse:
    catalogs = Catalog.objects.all()
    text = "<h1>"
    for catalog in catalogs:
        text += f"{catalog.name} </h1><br><h1>"
    return HttpResponse(text)


catalogs_list = catalog_list
