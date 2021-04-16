import datetime
import re
from itertools import takewhile

import yaml
from django.conf import settings as s
from yaml import YAMLError

from . import emoji
from . import pandoc

class ArticleError(Exception):
    def __init__(self, context):
        self.article_context = context


def get_article_paths():
    self = get_article_paths
    now=datetime.datetime.now() 
    five_minutes = datetime.timedelta(minutes=5)
    if self.paths is None or now - self.last_update > five_minutes:
        self.last_update = now
        get_article_paths.paths = list(s.BLOG_ARTICLE_PATH.glob(
            s.BLOG_DATE_GLOB_STRING + "-*/"))
        get_article_paths.paths.sort(reverse=True)
    return get_article_paths.paths
get_article_paths.paths = None

def post_processing(html,slug):
    html = re.sub("STATIC", slug, html)
    html = pandoc.pandoc2mathjax(html)
    html = emoji.slack2unicode(html)
    return html

def slug_to_title(slug):
    return slug.title().replace("-"," ")

def extract_date_and_slug_from_path(path):
    match = re.fullmatch("(\d{4})-(\d{2})-(\d{2})-(.*)", str(path.name))
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
            metadata = yaml.safe_load(string)
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
    paths = s.BLOG_ARTICLE_PATH.glob(s.BLOG_DATE_GLOB_STRING + "-" + slug + "/")
    try:
        return next(paths)
    except StopIteration:
        raise FileNotFoundError("No articles found")
