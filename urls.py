from django.urls import path

from . import views
from . import ajax
from . import filter_views

app_name = "blog"
urlpatterns = [
    path("", views.index, name="article-index"),
    path("page/<int:page>", views.index, name="article-index-page"),
    path("wip", views.wip_index, name="wip-index"),
    path("wip/<slug:slug>", views.wip_article, name="wip-article"),
    path("wip/<slug:slug>/<path:url>", views.wip_media),
    path("tags/<str:tag_string>", views.tags_view, name="tags"),
    path("tags/<str:tag_string>/page/<int:page>", views.tags_view, name="tags-page"),
    path("json/wip/<slug:slug>", ajax.wip),
    path("filter", filter_views.index, name="f-index"),
    path("filter/page/<int:page>", filter_views.index, name="f-index-page"),
    path("filter/wip", filter_views.wip_index, name="f-wip-index"),
    path("filter/wip/<slug:slug>", filter_views.wip_article, name="f-wip-article"),
    path("filter/wip/<slug:slug>/<path:url>", filter_views.article_media),
    path("filter/tags/<str:tag_string>", filter_views.tags_view, name="f-tags"),
    path("filter/<slug:slug>", filter_views.article_view, name="f-article"),
    path("filter/<slug:slug>/<path:url>", filter_views.article_media),
    path("filter/<slug:slug>.md", filter_views.md),
    path("filter/page/<int:page>", filter_views.index, name="f-index-page"),
    path("<slug:slug>", views.article_view, name="article"),
    path("<slug:slug>/<path:url>", views.article_media),
    path("<slug:slug>.md", views.md),
]

