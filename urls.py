from django.urls import path

from . import views

app_name = "blog"
urlpatterns = [
    path("", views.index, name="article-index"),
    path("wip", views.wip_index, name="wip-index"),
    path("wip/<slug:slug>", views.wip_article, name="wip-article"),
    path("page/<int:page>", views.index, name="article-index-page"),
    path("tags/<str:tag_string>", views.tags_view, name="tags"),
    path("tags/<str:tag_string>/page/<int:page>", views.tags_view, name="tags-page"),
    path("<slug:slug>", views.article_view, name="article"),
    path("<slug:slug>/<path:url>", views.media),
    path("<slug:slug>.md", views.md),
]
