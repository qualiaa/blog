from .base import CheckedFilter

from ..article import ArticleError
from ..article import extract_metadata, slug_to_title, post_processing
from ..article import extract_date_and_slug_from_path
from ..article import extract_stub
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

class Metadata(CheckedFilter):
    def __init__(self):
        super().__init__(inputs=["path","slug"], outputs="article")

    def __call__(self, request, context):
        path = context["path"]
        slug = context["slug"]

        markdown_path = path/s.MARKDOWN_FILENAME

        article_context = {
            "path": str(path),
            "title": slug_to_title(slug),
            "slug": slug,
            "markdown": markdown_path
        }
        if "date" in context: article_context["date"] = context["date"]

        if not markdown_path.exists():
            context["article"] = article_context
            e= ArticleError(article_context,
                    FileNotFoundError("Markdown file not found"))
            e.context = context
            raise e


        try: metadata = extract_metadata(markdown_path)
        except (YAMLError, IOError): metadata = {}
        article_context.update(metadata)

        context["article"] = article_context

        return request, context

class GetStub(CheckedFilter):
    def __init__(self):
        super().__init__(inputs="article", outputs="article")

    def __call__(self, request, context):
        markdown_path = context["article"]["markdown"]
        try:
            stub, stub_finished = extract_stub(markdown_path)
            html = pandoc.md2html(stub)
        except Exception as e:
            raise ArticleError(context["article"], e)
        slug = context["article"]["slug"]
        context["article"]["html"] = post_processing(html, slug)
        context["article"]["finished"] = stub_finished

        return request, context

class GetFullText(CheckedFilter):
    def __init__(self):
        super().__init__(inputs="article", outputs="article")

    def __call__(self, request, context):
        try:
            html = pandoc.md2html(context["article"]["markdown"])
            slug = context["article"]["slug"]
            context["article"]["html"] = post_processing(html, slug)
        except Exception as e:
            raise ArticleError(context["article"], e)

        return request, context
