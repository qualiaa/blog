from sys import stderr
from subprocess import CalledProcessError
from yaml import YAMLError

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
        paths = s.ARTICLE_PATH.glob(s.date_glob_string + "-" + context["slug"] + "/")
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
        super().__init__(inputs={"path","slug"}, outputs={"article","title"})

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
        context["title"] = article_context["title"]

        return request, context

class MetadataDangerous(CheckedFilter):
    def __init__(self):
        super().__init__(inputs="article", outputs={"article","title"})

    def __call__(self, request, context):
        markdown_path = context["article"]["markdown"]

        if not markdown_path.exists():
            e= ArticleError(context["article"])
                    
            e.context = context
            raise e from FileNotFoundError("Markdown file not found.")

        try: metadata = extract_metadata(markdown_path)
        except (YAMLError, IOError): metadata = {}
        if "tags" in metadata:
            metadata["tags"].sort()
            metadata["tags"] = [tag.replace("_"," ") for tag in metadata["tags"]]

        context["article"].update(metadata)
        context["title"] = context["article"]["title"]

        return request, context

class GetStub(CheckedFilter):
    def __init__(self):
        super().__init__(inputs="article", outputs="article")

    def __call__(self, request, context):
        markdown_path = context["article"]["markdown"]

        try:
            stub, stub_finished = extract_stub(markdown_path)
            bib_path = markdown_path.parent/"bib.bib"

            if bib_path.exists():
                html = pandoc.md2html(stub, bib_path)
            else:
                html = pandoc.md2html(stub)

            context["article"]["html"] = html
            context["article"]["finished"] = stub_finished
        except Exception as e:
            raise ArticleError(context["article"]) from e

        return request, context

class GetFullText(CheckedFilter):
    def __init__(self):
        super().__init__(inputs="article", outputs="article")

    def __call__(self, request, context):
        markdown_path = context["article"]["markdown"]
        bib_path = markdown_path.parent/"bib.bib"

        try:
            if bib_path.exists():
                html = pandoc.md2html(markdown_path, bib_path)
            else:
                html = pandoc.md2html(markdown_path)
        except CalledProcessError as e:
            print(e.stderr.decode('utf-8'),file=stderr)
            raise e
        except Exception as e:
            raise ArticleError(context["article"]) from e

        context["article"]["html"] = html

        return request, context
