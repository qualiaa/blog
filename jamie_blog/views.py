import datetime
import logging
import mimetypes

from django.conf import settings as s
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import HttpResponseServerError, HttpResponseRedirect, Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from .pipes.utils import CheckedLambda, Lambda
from .pipes.inputs import ContextInput, PublishedPaths
from .pipes.outputs import Render, Redirect
from .pipes.postprocessing import postprocessing
from .pipes.flow import For, Alternative, Either
from .pipes import cache as c
from .pipes import errors as e
from .pipes import article as a
from .pipes.Paginate import Paginate
from .pipes.sidebars import Sidebars
from .pipes.Tags import Tags

from . import article
from . import publish
from . import tag


def _return_file(request, path, url):
    if url.find("../") >= 0:
        return HttpResponseBadRequest("Invalid URL")
    if not path.exists():
        logging.warning("File not found: %s", path)
        raise Http404
    return HttpResponse(path.read_bytes(),
                        content_type=mimetypes.guess_type(url))


def _page_list(page):
    @Lambda
    def article_error(r, c):
        c["article"]["html"] = "Could not load article"
        return r, c
    return (
        Paginate(page=page, items_per_page=s.BLOG_ARTICLES_PER_PAGE)
        | For(over="paths",
              to="path",
              giving="article",
              result="article_list",
              f=(a.DateAndSlugFromPath()
                 | a.MetadataSafe()
                 | Alternative(a.MetadataDangerous(), article_error)
                 | Alternative(c.CachedText(stub=True),
                               Alternative(a.GetStub()
                                           | postprocessing()
                                           | c.CacheHTML(stub=True),
                                           article_error))))
        | Render("jamie_blog/index.html"))


def article_media(request, slug, url):
    try:
        path = article.path_from_slug(slug)/url
    except FileNotFoundError:
        raise Http404
    return _return_file(request, path, url)


def article_view(request, slug):
    se = e.ServerError
    return ContextInput(request, slug=slug) > (
        Sidebars(archive_paths=article.get_article_paths())
        | Either(a.SlugToPath(), e.NotFound("No article at this address"))
        | a.DateAndSlugFromPath()
        | a.MetadataSafe()
        | Either(a.MetadataDangerous(), se("Could not read file"))
        | Alternative(
            c.CachedText(),
            (
                Either(a.GetFullText(), se("Could not read file"))
                | Either(postprocessing(), se("Postprocessing error"))
                | Either(c.CacheHTML(), se("Cache error"))
            ))
        | Render("jamie_blog/article_view.html")
    )


def index(request, page=1):
    return PublishedPaths(request) > Sidebars() | _page_list(page)


def md(request, slug):
    path = article.path_from_slug(slug)
    text_path = article.get_text_path(path)
    if text_path.suffix == ".org":
        return redirect(f"{slug}.org", slug=slug)
    with text_path.open() as f:
        return HttpResponse(f.read(), content_type="text/markdown")


def org(request, slug):
    path = article.path_from_slug(slug)
    text_path = article.get_text_path(path)
    if text_path.suffix == ".md":
        return redirect(f"{slug}.md", slug=slug)
    with text_path.open() as f:
        return HttpResponse(f.read(), content_type="text/org")


def tags_view(request, tag_string, page=1):
    tag_list = tag_string.lower().split("+")

    @Lambda
    def error_msg(r, c):
        c["content"] = "<h2>No posts</h2>"
        return r, c

    return PublishedPaths(request) > (
        Sidebars()
        | Tags(tag_list)
        | Alternative(_page_list(page),
                      error_msg | Render("jamie_blog/simple.html")))


def wip_article(request, slug):
    path = s.BLOG_WIP_PATH/slug

    return_article = (
        a.MetadataDangerous()
        | Either(a.GetFullText(), e.ServerError("Pandoc Error"))
        | postprocessing() | Render("jamie_blog/wip/article.html"))

    @CheckedLambda
    def CheckAlreadyPublished(r, c):
        article.path_from_slug(slug)
        return r, c

    published_url = reverse("jamie_blog:article", kwargs={"slug": slug})

    return ContextInput(request, slug=slug, path=path, date=datetime.date.today()) > (
        a.MetadataSafe()
        | Alternative(return_article,
                      Either(CheckAlreadyPublished | Redirect(published_url),
                             e.NotFound)))


def wip_index(request):
    article_paths = [x for x in s.BLOG_WIP_PATH.iterdir()
            if x.is_dir() and
            (x/s.BLOG_MARKDOWN_FILENAME).exists()]
    article_paths.sort(key=lambda x: x.stat().st_mtime,reverse=True)
    article_names = [x.name for x in article_paths]

    return render(request, "jamie_blog/wip/index.html",
                  {"article_names": article_names})


def wip_media(request, slug, url):
    path = s.BLOG_WIP_PATH/slug/url

    return _return_file(request, path, url)


def publish_view(request, slug):
    try:
        publish.publish(slug)
    except FileNotFoundError as e:
        logging.error("Could not find article to publish: %s", e.args)
        return HttpResponseServerError("Could not find article")
    except FileExistsError as e:
        logging.error("Attempted to publish article twice: %s", e.args)
        return HttpResponseServerError("Article already published")

    return HttpResponseRedirect(reverse("jamie_blog:article",
                                        kwargs={"slug": slug}))


def tag_all_view(*args, **kargs):
    tag.tag_all()
    return HttpResponse(status=204)
