from django.http import JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from articles.forms import CommentForm
from articles.models import Article, Catalog


def _article_to_dict(article: Article) -> dict:
    return {
        "id": article.id,
        "title": article.title,
        "text": article.text,
        "rate": article.rate,
        "created_at": article.created_at.isoformat(),
    }


@require_GET
def api_articles_list(request: HttpRequest) -> JsonResponse:
    catalog_id = request.GET.get("catalog")
    qs = Article.objects.filter(catalog_id=catalog_id) if catalog_id else Article.objects.all()
    return JsonResponse([_article_to_dict(a) for a in qs], safe=False)


@require_GET
def api_article_detail(request: HttpRequest, pk: int) -> JsonResponse:
    article = Article.objects.filter(pk=pk).first()
    if article is None:
        return JsonResponse({"error": "Not found"}, status=404)
    return JsonResponse(_article_to_dict(article))


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


def article_detail(request: HttpRequest, pk: int) -> HttpResponse:
    article = get_object_or_404(Article, pk=pk)
    comments = article.comments.all()
    form = CommentForm()
    return render(
        request,
        "articles/article_detail.html",
        {
            "article": article,
            "comments": comments,
            "form": form,
        },
    )


@require_POST
def add_comment(request: HttpRequest, pk: int) -> HttpResponse:
    article = get_object_or_404(Article, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.save()
        return redirect("article_detail", pk=article.pk)

    comments = article.comments.all()
    return render(
        request,
        "articles/article_detail.html",
        {
            "article": article,
            "comments": comments,
            "form": form,
        },
    )

