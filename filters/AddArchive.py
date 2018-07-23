import datetime
from collections import defaultdict
from itertools import repeat

from django.urls import reverse

from .base import CheckedFilter
from .. import article


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
        archive_context = dict(zip((x.year for x in dates), repeat({})))

        for date in dates:
            archive_context[date.year][date.strftime("%B")] = []

        for date, slug, path in zip(*list(zip(*date_and_slug)),paths):
            title = article.slug_to_title(slug)
            markdown_path = path/article.MARKDOWN_FILENAME
            try:
                metadata = article.extract_metadata(markdown_path)
                title = metadata.get("title", title)
            except FileNotFoundError: pass
            url = reverse("blog:article",kwargs={"slug":slug})
            archive_context[date.year][date.strftime("%B")].append((url,title))

        context.update({"archive": archive_context})
        return request, context


