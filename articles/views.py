from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from articles.forms import CommentForm
from articles.models import Article, Catalog, Comment


def _article_to_dict(article: Article) -> dict:
    return {
        "id": article.id,
        "title": article.title,
        "text": article.text,
        "rate": article.rate,
        "created_at": article.created_at.isoformat(),
    }


class ApiArticlesListView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        catalog_id = request.GET.get("catalog")
        qs = Article.objects.filter(catalog_id=catalog_id) if catalog_id else Article.objects.all()
        return JsonResponse([_article_to_dict(a) for a in qs], safe=False)


class ApiArticleDetailView(View):
    def get(self, request: HttpRequest, pk: int) -> JsonResponse:
        article = Article.objects.filter(pk=pk).first()
        if article is None:
            return JsonResponse({"error": "Not found"}, status=404)
        return JsonResponse(_article_to_dict(article))


class ArticlesListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        count: int = Article.objects.all().count()
        text = "<h1>"
        for i in range(1, count + 1):
            article = Article.objects.filter(id=i).first()
            if article:
                text += f"{article.title} </h1><br><h1>"
        return HttpResponse(text)


class CatalogListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        catalogs = Catalog.objects.all()
        text = "<h1>"
        for catalog in catalogs:
            text += f"{catalog.name} </h1><br><h1>"
        return HttpResponse(text)


class ArticleDetailView(DetailView):
    model = Article
    template_name = "articles/article_detail.html"
    context_object_name = "article"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.all()
        context["form"] = CommentForm()
        return context


class AddCommentView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        article = get_object_or_404(Article, pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.user = request.user
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


class CommentEditView(LoginRequiredMixin, View):
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        comment = get_object_or_404(Comment, pk=kwargs["pk"])
        if comment.user != request.user:
            messages.error(request, "Это не ваш комментарий")
            return redirect("article_detail", pk=comment.article.pk)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        comment = get_object_or_404(Comment, pk=pk)
        form = CommentForm(instance=comment)
        return render(
            request,
            "articles/comment_edit.html",
            {
                "form": form,
                "comment": comment,
            },
        )

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        comment = get_object_or_404(Comment, pk=pk)
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("article_detail", pk=comment.article.pk)
        return render(
            request,
            "articles/comment_edit.html",
            {
                "form": form,
                "comment": comment,
            },
        )


class CommentDeleteView(LoginRequiredMixin, View):
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        comment = get_object_or_404(Comment, pk=kwargs["pk"])
        if comment.user != request.user:
            messages.error(request, "Это не ваш комментарий")
            return redirect("article_detail", pk=comment.article.pk)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        comment = get_object_or_404(Comment, pk=pk)
        return render(
            request,
            "articles/comment_confirm_delete.html",
            {
                "comment": comment,
            },
        )

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        comment = get_object_or_404(Comment, pk=pk)
        article_pk = comment.article.pk
        comment.delete()
        return redirect("article_detail", pk=article_pk)


class MyCommentsView(LoginRequiredMixin, ListView):
    model = Comment
    template_name = "articles/my_comments.html"
    context_object_name = "comments"

    def get_queryset(self):
        return self.request.user.comments.select_related("article").all()


api_articles_list = ApiArticlesListView.as_view()
api_article_detail = ApiArticleDetailView.as_view()
articles_list = ArticlesListView.as_view()
catalog_list = CatalogListView.as_view()
catalogs_list = catalog_list
article_detail = ArticleDetailView.as_view()
add_comment = AddCommentView.as_view()
edit_comment = CommentEditView.as_view()
delete_comment = CommentDeleteView.as_view()
my_comments = MyCommentsView.as_view()
