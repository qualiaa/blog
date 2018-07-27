import re
from itertools import chain

from django.http import Http404

from .base import CheckedFilter
from ..tag import get_articles_for_tag

class Tags(CheckedFilter):
    def __init__(self, tags : [str]):
        super().__init__(outputs="paths")
        self.tags = tags

        # TODO raise sensible error
        if not all(re.match("[A-Za-z_]",x) for x in self.tags):
            raise ValueError("Invalid tag in {}".format(self.tags))

    def __call__(self, request, context):
        article_paths = chain(*[get_articles_for_tag(t) for t in self.tags])
        article_paths = set(article_paths)

        if "paths" in context:
            paths = set(path.resolve() for path in context["paths"])
            article_paths = article_paths.intersection(paths)

        context["paths"] = article_paths

        return request, context
