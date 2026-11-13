"""
URL configuration for blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from articles.views import (
    add_comment,
    api_article_detail,
    api_articles_list,
    article_detail,
    articles_list,
    catalog_list,
    delete_comment,
    edit_comment,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", articles_list),
    path("catalog/", catalog_list),
    path("catalogs/", catalog_list),
    path("articles/<int:pk>/", article_detail, name="article_detail"),
    path("articles/<int:pk>/comment/", add_comment, name="add_comment"),
    path("comments/<int:pk>/edit/", edit_comment, name="edit_comment"),
    path("comments/<int:pk>/delete/", delete_comment, name="delete_comment"),
    path("api/articles/", api_articles_list),
    path("api/articles/<int:pk>/", api_article_detail),
]
