import datetime
import re
from itertools import takewhile

import yaml
from django.conf import settings as s

from . import emoji
from . import pandoc


class ArticleError(Exception):
    def __init__(self, context, *args):
        self.article_context = context
        super().__init__(*args, context)


def get_article_paths():
    self = get_article_paths
    now = datetime.datetime.now()
    five_minutes = datetime.timedelta(minutes=5)
    if self.paths is None or now - self.last_update > five_minutes:
        self.last_update = now
        get_article_paths.paths = list(s.BLOG_ARTICLE_PATH.glob(
            s.BLOG_DATE_GLOB_STRING + "-*/"))
        get_article_paths.paths.sort(reverse=True)
    return get_article_paths.paths
get_article_paths.paths = None


def post_processing(html, slug):
    html = re.sub("STATIC", slug, html)
    html = pandoc.pandoc2mathjax(html)
    html = emoji.slack2unicode(html)
    return html


def slug_to_title(slug):
    return slug.title().replace("-", " ")


def extract_date_and_slug_from_path(path):
    match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})-(.*)", str(path.name))
    date = map(int, match.groups()[:3])
    slug = match.groups()[-1]
    return datetime.date(*date), slug


def extract_metadata(text_path):
    try:
        f = {
            ".md": _extract_metadata_md,
            ".org": _extract_metadata_org
        }[text_path.suffix]
    except KeyError:
        raise ValueError(f"text_path must be .org or .md file, got {text_path}")
    return f(text_path)


def _extract_metadata_md(markdown_path):
    delimiter = "---"
    metadata = {}
    with markdown_path.open() as f:
        if next(f).startswith(delimiter):
            string = "".join(takewhile(lambda x: not x.startswith(delimiter),
                                       f))
            metadata = yaml.safe_load(string)
    return metadata


def _parse_org_metadata_value(v):
    lower = v.lower()
    if re.fullmatch("t(rue)?", lower):
        return True
    if re.fullmatch("f(alse)?", lower):
        return False
    if re.fullmatch(r"\[[^]]*\]", v):
        return [_parse_org_metadata_value(element.strip())
                for element in v[1:-1].split(",")]
    return v


def _extract_metadata_org(org_path):
    metadata = {}
    with org_path.open() as f:
        for line in f:
            if re.match(r"^\s*$", line):
                continue
            if not line.startswith("#"):
                break
            kv_match = re.match(r"^#\+(\S+):", line)
            if kv_match:
                key = kv_match[1].lower()
                value = line.split(":", maxsplit=1)[1].strip()
                metadata[key] = _parse_org_metadata_value(value)
    return metadata


def _extract_stub(text_path, delim_regex):
    finished = False
    with text_path.open() as file:
        stub = list(takewhile(
                lambda line: re.match(delim_regex, line) is None, file))
        if next(file, None) is None:
            finished = True
    stub = "".join(stub)
    return stub, finished


def extract_stub(text_path):
    try:
        delim = {
            ".md": "^ *<!-- *break *--> *$",
            ".org": "^# *break *$"
        }[text_path.suffix]
    except KeyError:
        raise ValueError(f"text_path must be .org or .md file, got {text_path}")
    return _extract_stub(text_path, re.compile(delim))


def path_from_slug(slug):
    # TODO: Handle case of multiple matches
    paths = s.BLOG_ARTICLE_PATH.glob(s.BLOG_DATE_GLOB_STRING + "-" + slug + "/")
    try:
        return next(paths)
    except StopIteration:
        raise FileNotFoundError("No articles found")


def get_text_path(folder_path):
    article_path = folder_path/s.BLOG_ARTICLE_FILENAME
    markdown_path = article_path.with_suffix(".md")
    org_path = article_path.with_suffix(".org")
    if markdown_path.exists():
        return markdown_path
    elif org_path.exists():
        return org_path
    raise FileNotFoundError(
        f"{folder_path} has no article file "
        f"(tried {article_path}.md and {article_path}.org)")
