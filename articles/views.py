from django.http.request import HttpRequest
from django.http.response import HttpResponse

from articles.models import Article


def articles_list(request: HttpRequest) -> HttpResponse:
    count: int = Article.objects.all().count()
    text = "<h1>"
    for i in range(1, count + 1):
        article = Article.objects.filter(id=i).first()
        text += f"{article.title} </h1><br><h1>"
    return HttpResponse(text)
