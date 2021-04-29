import re
from itertools import chain

from django.http import Http404

from .base import CheckedPipe
from ..tag import Tag

class Tags(CheckedPipe):
    def __init__(self, tag_names: [str]):
        super().__init__(outputs={"paths", "tags", "title"})
        self.tags = [Tag(t) for t in tag_names]

        # TODO raise sensible error
        if not all(re.match("[A-Za-z_]",x) for x in self.tags):
            raise ValueError("Invalid tag in {}".format(self.tags))

    def __call__(self, request, context):
        article_paths = chain(*[t.article_paths for t in self.tags])
        article_paths = set(article_paths)

        if "paths" in context:
            paths = set(path.resolve() for path in context["paths"])
            article_paths = article_paths.intersection(paths)

        context["paths"] = article_paths
        context["tags"] = self.tags
        context["title"] = "Tags: "+", ".join(self.tags).replace("_"," ").title()

        return request, context
