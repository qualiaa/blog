import re

from django.conf import settings as s

from ..pandoc import pandoc2mathjax
from .base import CheckedPipe


class PandocToMathJax(CheckedPipe):
    def __init__(self):
        super().__init__(inputs="article", outputs="article")

    def __call__(self, request, context):
        context["article"]["html"] = pandoc2mathjax(context["article"]["html"])
        return request, context


class ResolveLocalURLs(CheckedPipe):
    def __init__(self):
        super().__init__(inputs="article", outputs="article")

    def __call__(self, request, context):
        slug = context["article"]["slug"]
        html = context["article"]["html"]
        context["article"]["html"] = re.sub(s.BLOG_TEMPLATE_LOCAL_URL, slug, html)
        return request, context


def postprocessing():
    return ResolveLocalURLs()
