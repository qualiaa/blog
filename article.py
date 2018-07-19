import datetime
import pathlib
import re
from itertools import takewhile

import yaml
from yaml import YAMLError

from . import pandoc

MARKDOWN_FILENAME = "article.md"
ARTICLE_PATH=pathlib.Path("blog/articles/")
WIP_PATH = ARTICLE_PATH/"wip"
date_glob_string = "{}-{}-{}".format("[0-9]" * 4,"[0-9]" * 2, "[0-9]" * 2)

class ArticleError(Exception):
    def __init__(self, context, e):
        self.article_context = context
        self.exception = e


def get_article_paths():
    if get_article_paths.paths is None:
        get_article_paths.paths = list(ARTICLE_PATH.glob(date_glob_string + "_*/"))
        get_article_paths.paths.sort(reverse=True)
    return get_article_paths.paths
get_article_paths.paths = None

def post_processing(html,slug):
    html = re.sub("STATIC", slug, html)
    html = re.sub("<span class=\"math inline\">"+re.escape(r"\(")+
                   "(.*)" + re.escape(r"\)") + "</span>",
            "<script type=\"math/tex\">\g<1></script>", html)
    html = re.sub("<span class=\"math display\">"+re.escape(r"\[")+
                   "(.*)" + re.escape(r"\]") + "</span>",
            "<script type=\"math/tex; mode=display\">\g<1></script>", html)
    return html
        #str(pathlib.Path(settings.STATIC_URL)/"blog"/slug),html)

def slug_to_title(slug):
    return slug.title().replace("_"," ")

def extract_date_and_slug_from_path(path):
    match = re.fullmatch("(\d{4})-(\d{2})-(\d{2})_(.*)", str(path.name))
    y,m,d = [int(x) for x in match.groups()[:3]]
    slug = match.groups()[-1]

    return datetime.date(y,m,d), slug

    # XXX: Python 3.7 Only
    #return datetime.fromisoformat(date_string), slug

def extract_metadata(markdown_path):
    delimiter = "---"
    metadata = {}
    with markdown_path.open() as f:
        if next(f).startswith(delimiter):
            lines = list(takewhile(lambda x: not x.startswith(delimiter), f))
            string = "".join(lines)
            metadata = yaml.load(string)
    return metadata

def extract_stub(markdown_path):
    finished = False
    with markdown_path.open() as markdown_file:
        stub = list(takewhile(
            lambda line: re.match("^ *<!-- *break *--> *$",
                line) is None,
            markdown_file))
        try: next(markdown_file)
        except: finished = True
    stub = "".join(stub)
    return stub, finished

def path_from_slug(slug):
    # TODO: Handle case of multiple matches
    paths = ARTICLE_PATH.glob(date_glob_string + "_" + slug + "/")
    try:
        return next(paths)
    except StopIteration:
        raise FileNotFoundError("No articles found")

def get_context(slug=None, path=None, generate_stub=False):
    if path is None and slug is None:
        raise ValueError("Must provide one of slug or path")
    elif path is None:
        path = path_from_slug(slug)
    if slug is None:
        date, slug = extract_date_and_slug_from_path(path)
    else:
        date, _ = extract_date_and_slug_from_path(path)

    article_context = {
        "path": str(path),
        "slug": slug,
        "title": slug_to_title(slug),
        "date": date,
    }

    markdown_path = path/MARKDOWN_FILENAME

    if not markdown_path.exists():
        raise ArticleError(article_context,
                FileNotFoundError("Markdown file not found"))

    try: metadata = extract_metadata(markdown_path)
    except (YAMLError, IOError): metadata = {}

    try:
        if generate_stub:
            stub, stub_finished = extract_stub(markdown_path)
            html = pandoc.md2html(stub)
            article_context["finished"] = stub_finished
        else:
            html = pandoc.md2html(markdown_path)

        html = post_processing(html, slug)
    except Exception as e:
        raise ArticleError(article_context, e)

    article_context.update({
        "html": html
    })
    article_context.update(metadata)

    return article_context

def get_wip_context(slug):
    path = WIP_PATH/slug
    markdown_path = path/MARKDOWN_FILENAME

    try:
        metadata = extract_metadata(markdown_path)
    except (YAMLError, IOError):
        metadata = {}

    html = pandoc.md2html(markdown_path)
    html = post_processing(html, slug)
    article_context = {
        "html": html,
        "path": path,
        "slug": slug,
        "title": slug_to_title(slug)
    }
    article_context.update(metadata)
    return article_context
