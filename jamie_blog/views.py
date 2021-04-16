import datetime
import mimetypes

from django.http import HttpResponse, HttpResponseBadRequest
from django.http import HttpResponseServerError, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse

from .filters.utils import CheckedLambda,Lambda
from .filters.inputs import ContextInput, PublishedPaths
from .filters.outputs import Render, Redirect
from .filters.postprocessing import postprocessing
from .filters.flow import For, Alternative, Either
from .filters import cache as c
from .filters import errors as e
from .filters import article as a
from .filters.Paginate import Paginate
from .filters.sidebars import Sidebars
from .filters.Tags import Tags

from . import article
from . import settings as s
from . import publish
from . import tag

def _return_file(request, path, url):
    if url.find("../") >= 0:
        return HttpResponseBadRequest("Invalid URL")
    if not path.exists():
        print(str(path))
        raise Http404
    return HttpResponse(path.read_bytes(), content_type=mimetypes.guess_type(url))

def _page_list(page):
    @Lambda
    def article_error(r, c):
        c["article"]["html"] = "Could not load article"
        return r, c
    return \
            Paginate(page=page, items_per_page=s.ARTICLES_PER_PAGE) |\
            For(over="paths",
                to="path",
                giving="article",
                result="article_list",
                f=a.DateAndSlugFromPath() | a.MetadataSafe() |
                    Alternative(a.MetadataDangerous(), article_error) |
                    Alternative(c.CachedText(stub=True),
                        Alternative(a.GetStub() |
                                postprocessing() |
                                c.CacheHTML(stub=True),
                            article_error)))                        |\
            Render("jamie_blog/index.html")

def article_media(request, slug, url):
    try:
        path = article.path_from_slug(slug)/url
    except FileNotFoundError:
        raise Http404

    return _return_file(request, path, url)

def article_view(request, slug):
    se = e.ServerError
    return ContextInput(request, slug=slug)                       >\
            Sidebars(archive_paths=article.get_article_paths())   |\
            Either(a.SlugToPath(), e.NotFound())                  |\
            a.DateAndSlugFromPath()                               |\
            a.MetadataSafe()                                      |\
            Either(a.MetadataDangerous(),
                   se("Could not read file"))                     |\
            Alternative(c.CachedText(),
                        Either(a.GetFullText(), se("Could not read file")) |
                            Either(postprocessing(), se("Postprocessing error")) |
                            Either(c.CacheHTML(), se("Cache error"))) |\
            Render("jamie_blog/article_view.html")

def index(request, page=1):
    return PublishedPaths(request) >\
            Sidebars()             |\
            _page_list(page)

def md(request, slug):
    path = article.path_from_slug(slug)
    markdown_path = path/s.MARKDOWN_FILENAME
    with markdown_path.open() as f:
        return HttpResponse(f.read(),content_type="text/markdown")

def tags_view(request, tag_string, page=1):
    tag_list = tag_string.lower().split("+")

    @Lambda
    def error_msg(r,c):
        c["content"] = "<h2>No posts</h2>"
        return r,c

    return PublishedPaths(request) >\
            Sidebars()             |\
            Tags(tag_list)         |\
            Alternative(_page_list(page),
                error_msg |
                Render("jamie_blog/simple.html"))


def wip_article(request, slug):
    path = s.WIP_PATH/slug

    return_article = a.MetadataDangerous() |\
            Either(a.GetFullText(), e.ServerError("Pandoc Error")) |\
            postprocessing() | Render("jamie_blog/wip/article.html")

    @CheckedLambda
    def CheckAlreadyPublished(r,c):
        article.path_from_slug(slug)
        return r, c

    published_url = reverse("jamie_blog:article",kwargs={"slug": slug})

    return ContextInput(request, slug=slug, path=path, date=datetime.date.today()) >\
            a.MetadataSafe() |\
            Alternative(return_article,
                Either(CheckAlreadyPublished | Redirect(published_url),
                    e.NotFound))

def wip_index(request):
    article_paths = [x for x in s.WIP_PATH.iterdir()
            if x.is_dir() and
            (x/s.MARKDOWN_FILENAME).exists()]
    article_paths.sort(key=lambda x: x.stat().st_mtime,reverse=True)
    article_names = [x.name for x in article_paths]

    return render(request, "jamie_blog/wip/index.html",
            {"article_names": article_names})

def wip_media(request, slug, url):
    path = s.WIP_PATH/slug/url

    return _return_file(request, path, url)

def publish_view(request, slug):
    try:
        publish.publish(slug)
    except FileNotFoundError as e:
        print(e.args)
        return HttpResponseServerError("Could not find article")
    except FileExistsError as e:
        print(e.args)
        return HttpResponseServerError("Article already published")

    return HttpResponseRedirect(reverse("jamie_blog:article",kwargs={"slug":slug}))

def tag_all_view(*args,**kargs):
    tag.tag_all()
    return HttpResponse(status=204)
