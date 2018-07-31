import mimetypes

from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render

from .filters.utils import Lambda
from .filters.inputs import ContextInput, PublishedPaths
from .filters.outputs import Render
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
            Render("blog/index.html")

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
            Render("blog/article_view.html")

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

    return PublishedPaths(request) >\
            Sidebars()             |\
            Tags(tag_list)         |\
            _page_list(page)

def wip_article(request, slug):
    path = s.WIP_PATH/slug
    return ContextInput(request, slug=slug, path=path) >\
            a.MetadataSafe()                           |\
            a.MetadataDangerous()                      |\
            a.GetFullText()                            |\
            postprocessing()                           |\
            Render("blog/wip/article.html")

def wip_index(request):
    article_names = [x.name for x in s.WIP_PATH.iterdir()
            if x.is_dir() and
            (x/s.MARKDOWN_FILENAME).exists()]

    return render(request, "blog/wip/index.html",
            {"article_names": article_names})

def wip_media(request, slug, url):
    path = s.WIP_PATH/slug/url

    return _return_file(request, path, url)
