import logging
from subprocess import CalledProcessError

from django.conf import settings as s
from yaml import YAMLError

from .. import pandoc
from ..article import (
    extract_metadata,
    slug_to_title,
    ArticleError,
    extract_date_and_slug_from_path,
    extract_stub,
    get_text_path
)
from . import errors as e
from .base import CheckedPipe


class SlugToPath(CheckedPipe):
    def __init__(self):
        super().__init__(inputs="slug", outputs="path")

    def __call__(self, request, context):
        # TODO: Handle case of multiple matches
        paths = s.BLOG_ARTICLE_PATH.glob(
                s.BLOG_DATE_GLOB_STRING + "-" + context["slug"] + "/")
        try:
            context["path"] = next(paths)
        except StopIteration:
            raise e.NotFound("No articles found")
        return request, context


class DateAndSlugFromPath(CheckedPipe):
    def __init__(self):
        super().__init__(inputs="path", outputs=["slug", "date"])

    def __call__(self, request, context):
        date, slug = extract_date_and_slug_from_path(context["path"])
        context["date"] = date
        if "slug" not in context:
            context["slug"] = slug

        return request, context


class MetadataSafe(CheckedPipe):
    def __init__(self):
        super().__init__(inputs={"path", "slug"},
                         outputs={"article", "title"})

    def __call__(self, request, context):
        path = context["path"]
        slug = context["slug"]

        article_context = {
            "path": path,
            "path_string": str(path),
            "title": slug_to_title(slug),
            "slug": slug,
        }
        if "date" in context:
            article_context["date"] = context["date"]

        context["article"] = article_context
        context["title"] = article_context["title"]

        return request, context


class MetadataDangerous(CheckedPipe):
    def __init__(self):
        super().__init__(inputs="article", outputs={"article", "title"})

    def __call__(self, request, context):
        try:
            text_path = get_text_path(context["article"]["path"])
        except FileNotFoundError as e:
            raise e.NotFound(*e.args)
        context["article"]["text_path"] = text_path

        try:
            metadata = extract_metadata(text_path)
        except (YAMLError, IOError):
            raise e.ServerError("Invalid article metadata")
        if "tags" in metadata:
            metadata["tags"].sort()
            metadata["tags"] = [
                tag.replace("_", " ") for tag in metadata["tags"]]

        context["article"].update(metadata)
        context["title"] = context["article"]["title"]
        return request, context


_text_converters = {
    ".org": pandoc.org2html,
    ".md": pandoc.md2html
}


class GetStub(CheckedPipe):
    def __init__(self):
        super().__init__(inputs="article", outputs="article")

    def __call__(self, request, context):
        text_path = context["article"]["text_path"]

        try:
            stub, stub_finished = extract_stub(text_path)
            bib_path = context["article"]["path"]/"bib.bib"

            stub_fn = _text_converters[text_path.suffix]
            html = stub_fn(stub, bib_path if bib_path.exists() else None)

            context["article"]["html"] = html
            context["article"]["finished"] = stub_finished
        except CalledProcessError as e:
            logging.error("Pandoc error processing %s", text_path)
            logging.error("%s", e.stderr.decode('utf-8'))
            raise e
        except Exception as e:
            raise ArticleError(context["article"], e) from e
        return request, context


class GetFullText(CheckedPipe):
    def __init__(self):
        super().__init__(inputs="article", outputs="article")

    def __call__(self, request, context):
        text_path = context["article"]["text_path"]
        bib_path = context["article"]["path"]/"bib.bib"

        try:
            conv_fn = _text_converters[text_path.suffix]
            html = conv_fn(text_path, bib_path if bib_path.exists() else None)
        except CalledProcessError as e:
            logging.error("Pandoc error processing %s", text_path)
            logging.error("%s", e.stderr.decode('utf-8'))
            raise e
        except Exception as e:
            raise ArticleError(context["article"], e) from e

        context["article"]["html"] = html

        return request, context
