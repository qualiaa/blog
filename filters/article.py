from .base import CheckedFilter

from ..article import ArticleError
from ..article import extract_metadata, slug_to_title
from ..article import extract_date_and_slug_from_path, extract_stub
from .. import pandoc
from .. import settings as s


class SlugToPath(CheckedFilter):
    def __init__(self):
        super().__init__(inputs="slug", outputs="path")

    def __call__(self, request, context):
        # TODO: Handle case of multiple matches
        paths = s.ARTICLE_PATH.glob(s.date_glob_string + "_" + context["slug"] + "/")
        try:
            context["path"] = next(paths)
        except StopIteration:
            raise FileNotFoundError("No articles found")

        return request, context

class DateAndSlugFromPath(CheckedFilter):
    def __init__(self):
        super().__init__(inputs="path", outputs=["slug","date"])

    def __call__(self, request, context):
        date, slug = extract_date_and_slug_from_path(context["path"])
        context["date"] = date
        if "slug" not in context: context["slug"] = slug

        return request, context

class MetadataSafe(CheckedFilter):
    def __init__(self):
        super().__init__(inputs=["path","slug"], outputs="article")

    def __call__(self, request, context):
        path = context["path"]
        slug = context["slug"]

        article_context = {
            "path": path,
            "path_string": str(path),
            "title": slug_to_title(slug),
            "slug": slug,
            "markdown": path/s.MARKDOWN_FILENAME
        }
        if "date" in context: article_context["date"] = context["date"]

        context["article"] = article_context

        return request, context

class MetadataDangerous(CheckedFilter):
    def __init__(self):
        super().__init__(inputs="article", outputs="article")

    def __call__(self, request, context):
        markdown_path = context["article"]["markdown"]

        if not markdown_path.exists():
            e= ArticleError(context["article"],
                    FileNotFoundError("Markdown file not found."))
            e.context = context
            raise e

        try: metadata = extract_metadata(markdown_path)
        except (YAMLError, IOError): metadata = {}

        context["article"].update(metadata)

        return request, context

class GetStub(CheckedFilter):
    def __init__(self):
        super().__init__(inputs="article", outputs="article")

    def __call__(self, request, context):
        markdown_path = context["article"]["markdown"]
        try:
            stub, stub_finished = extract_stub(markdown_path)
            context["article"]["html"] = pandoc.md2html(stub)
            context["article"]["finished"] = stub_finished
        except Exception as e:
            raise ArticleError(context["article"], e)

        return request, context

class GetFullText(CheckedFilter):
    def __init__(self):
        super().__init__(inputs="article", outputs="article")

    def __call__(self, request, context):
        try:
            context["article"]["html"] = pandoc.md2html(context["article"]["markdown"])
        except Exception as e:
            raise ArticleError(context["article"], e)

        return request, context
