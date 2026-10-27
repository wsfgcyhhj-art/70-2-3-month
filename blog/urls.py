from django.contrib import admin
from django.urls import path
from articles.views import hello_world, hello_name, about

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", hello_world),
    path("hello/<str:name>", hello_name),
    path("about/", about),
]
