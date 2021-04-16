import datetime
from collections import defaultdict
from itertools import repeat
import hashlib

from django.conf import settings as s
from django.urls import reverse

from .base import CheckedFilter
from .. import article

class AddTagbar(CheckedFilter):
    def __call__(self, request, context):
        tags = sorted([tag.name for tag in s.BLOG_TAG_PATH.iterdir()])
        tags = [{"slug": x,
                 "name": x.replace("_"," ").title(),
                 "url": reverse("jamie_blog:tags", kwargs={"tag_string":x})
                 } for x in tags]

        for i, tag in enumerate(tags):
            try:
                tag["color"] = s.BLOG_TAG_COLORS[i]
            except IndexError:
                h = hashlib.blake2s(tag["slug"].encode())
                v = int.from_bytes(h.digest(), byteorder="big")
                tag["color"] = (v & 0xFF, (v & 0xFF00) >> 8, (v & 0xFF0000) >> 16)

        context.update({"all_tags": tags})
        return request, context


class AddArchive(CheckedFilter):
    def __init__(self, archive_paths=None):
        inputs = {}
        if archive_paths is None:
            inputs = "paths"
        else:
            self.archive_paths = archive_paths
        
        super().__init__(inputs=inputs,outputs="archive")

    def __call__(self, request, context):
        if hasattr(self,"archive_paths"):
            paths = self.archive_paths
        elif "paths" in context:
            paths = context["paths"]
        else: raise ValueError()

        # TODO: rest of this

        date_and_slug = [article.extract_date_and_slug_from_path(x) for x in paths]
        dates = set(datetime.date(x.year,x.month, 1) for x, _ in date_and_slug)
        dates = sorted(list(dates),reverse=True)
        archive_context = {}

        for date in dates:
            archive_context.setdefault(date.year,{})[date.strftime("%B")] = []

        for date, slug, path in zip(*list(zip(*date_and_slug)),paths):
            title = article.slug_to_title(slug)
            markdown_path = path/s.BLOG_MARKDOWN_FILENAME
            try:
                metadata = article.extract_metadata(markdown_path)
                title = metadata.get("title", title)
            except FileNotFoundError: pass
            url = reverse("jamie_blog:article",kwargs={"slug":slug})
            archive_context[date.year][date.strftime("%B")].append((url,title))
            #print(archive_context.items())

        context.update({"archive": archive_context})
        return request, context


def Sidebars(archive_paths=None):
    return AddArchive(archive_paths) | AddTagbar()
