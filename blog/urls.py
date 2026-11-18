from django.contrib import admin
from django.urls import path

from articles.views import (
    AddCommentView,
    ApiArticleDetailView,
    ApiArticlesListView,
    ArticleDetailView,
    ArticlesListView,
    CatalogListView,
    CommentDeleteView,
    CommentEditView,
    MyCommentsView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", ArticlesListView.as_view(), name="articles_list"),
    path("catalog/", CatalogListView.as_view(), name="catalog_list"),
    path("catalogs/", CatalogListView.as_view()),
    path("articles/<int:pk>/", ArticleDetailView.as_view(), name="article_detail"),
    path("articles/<int:pk>/comment/", AddCommentView.as_view(), name="add_comment"),
    path("comments/<int:pk>/edit/", CommentEditView.as_view(), name="edit_comment"),
    path("comments/<int:pk>/delete/", CommentDeleteView.as_view(), name="delete_comment"),
    path("my-comments/", MyCommentsView.as_view(), name="my_comments"),
    path("my-comments", MyCommentsView.as_view()),
    path("api/articles/", ApiArticlesListView.as_view(), name="api_articles_list"),
    path("api/articles/<int:pk>/", ApiArticleDetailView.as_view(), name="api_article_detail"),
]
