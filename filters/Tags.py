from itertools import chain

from .base import CheckedFilter
from ..tag import get_articles_for_tag

class Tags(CheckedFilter):
    def __init__(self, tags : [str]):
        super().__init__(outputs="paths")
        # XXX: Should this take tag string?
        #tag_list = tag_string.lower().split("+")
        self.tags = tags

        # TODO raise sensible error
        if not all(x.isalpha() for x in self.tags):
            raise Http404

    def __call__(self, request, context):
        article_paths = chain(*[get_articles_for_tag(t) for t in self.tags])
        article_paths = set(article_paths)

        if "paths" in context:
            paths = set(path.resolve() for path in context["paths"])
            article_paths = article_paths.intersection(paths)

        #raise RuntimeError("{}".format(article_paths))
        context["paths"] = article_paths

        return request, context
