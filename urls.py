from django.urls import path

from . import views

app_name = "blog"
urlpatterns = [
    path("", views.index, name="index"),
    path("page/<int:page>", views.index, name="index-page"),
    path("tags/<str:tag_string>", views.tags_view, name="tags"),
    path("tags/<str:tag_string>/page/<int:page>", views.tags_view, name="tags-page"),
    path("<slug:slug>", views.article_view, name="article"),
    path("<slug:slug>/<path:url>", views.media),
    path("<slug:slug>.md", views.md),
]
