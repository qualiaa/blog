import mimetypes
import re
from subprocess import CalledProcessError
from itertools import takewhile, chain

from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseServerError, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse

from . import archive
from . import article
from .article import ArticleError
from . import tag

ARTICLES_PER_PAGE = 5

def _return_file(request, path, url):
    if url.find("../") >= 0:
        return HttpResponseBadRequest("Invalid URL")
    if not path.exists():
        raise Http404
    return HttpResponse(path.read_bytes(), content_type=mimetypes.guess_type(url))

def article_media(request, slug, url):
    try:
        path = article.path_from_slug(slug)/url
    except FileNotFoundError:
        raise Http404

    return _return_file(request, path, url)



def _show_article_list(request, article_paths, page=1):
    context = {"page": {}} 
    article_paths = sorted(list(article_paths), reverse=True)

    num_pages = len(article_paths) // ARTICLES_PER_PAGE + 1
    page_index = page - 1
    if page_index < 0 or page_index >= num_pages:
        raise Http404

    url_name = request.resolver_match.url_name
    url_name = "blog:" + url_name
    if url_name.find("page") < 0: url_name += "-page"
    if page > 1:
        context["page"]["prev"] = reverse(url_name, kwargs={"page":page-1})
    if page < num_pages:
        context["page"]["next"] = reverse(url_name, kwargs={"page":page+1})

    start_article = (page_index-1)*ARTICLES_PER_PAGE


    article_paths = article_paths[
        page_index*ARTICLES_PER_PAGE:(page_index+1)*ARTICLES_PER_PAGE]
    article_contexts = []
    for path in article_paths:
        # TODO: rewrite this wtf
        try:
            try:
                article_context = article.get_context(path=path, generate_stub=True)
            except ArticleError as e:
                article_context = e.article_context
                raise e.exception
        except FileNotFoundError as e:
            article_context["html"] = "<p>File not found</p>"
        except IOError:
            article_context["html"] = "<p>Could not read content</p>"
        except ValueError as e:
            return HttpResponseServerError("Invalid request")
        except CalledProcessError:
            article_context["html"] = "<p>Error preparing content</p>"

        article_contexts.append(article_context)

    context.update(archive.context())
    context.update({
        "article_list": article_contexts,
    })

    return render(request, "blog/index.html", context)

def index(request, *args, **kargs):
    article_paths = article.get_article_paths()
    return _show_article_list(request, article_paths, *args, **kargs)

def tags_view(request, tag_string, *args, **kargs):
    tag_list = tag_string.lower().split("+")
    if not all(x.isalpha() for x in tag_list):
        raise Http404

    # TODO: rewrite this when it's not 4am
    try:
        article_paths = chain(*[tag.get_articles_for_tag(t) for t in tag_list])
        article_paths = set(article_paths)
    except FileNotFoundError:
        raise Http404

    return _show_article_list(request, article_paths, *args, **kargs)


def md(request, slug):
    path = article.path_from_slug(slug)
    markdown_path = path/article.MARKDOWN_FILENAME
    with markdown_path.open() as f:
        return HttpResponse(f.read(),content_type="text/markdown")

def article_view(request, slug):
    # TODO: rewrite this wtf
    try:
        try:
            article_context = article.get_context(slug=slug)
        except ArticleError as e:
            article_context = e.article_context
            raise e.exception
    except FileNotFoundError as e:
        raise Http404
    except IOError as e:
        return HttpResponseServerError("IO Error")
    except ValueError as e:
        return HttpResponseServerError("Invalid request")
    except CalledProcessError as e:
        err_msg = "Error preparing file."
        if settings.DEBUG:
            err_msg += "\n" + e.cmd + "\n" + e.stderr
        return HttpResponseServerError(err_msg)

    context = {
        "article": article_context,
        "title": article_context["title"],
    }
    context.update(archive.context())

    return render(request, "blog/article_view.html", context)

def wip_index(request):
    article_names = [x.name for x in article.WIP_PATH.iterdir()
            if x.is_dir() and
            (x/article.MARKDOWN_FILENAME).exists()]

    return render(request, "blog/wip/index.html",
            {"article_names": article_names})

def wip_article(request, slug):
    article_context = article.get_wip_context(slug)
    context = {
        "article": article_context,
        "title": article_context["title"],
    }

    return render(request, "blog/wip/article.html", context)

def wip_media(request, slug, url):
    path = article.WIP_PATH/slug/url

    return _return_file(request, path, url)
