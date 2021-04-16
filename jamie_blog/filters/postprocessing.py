import re

from django.conf import settings as s

from ..pandoc import pandoc2mathjax
from ..emoji import slack2unicode
from .base import CheckedFilter

class PandocToMathJax(CheckedFilter):
    def __init__(self):
        super().__init__(inputs="article",outputs="article")
    
    def __call__(self, request, context):
        context["article"]["html"] = pandoc2mathjax(context["article"]["html"])
        return request, context

class SlackToUnicode(CheckedFilter):
    def __init__(self):
        super().__init__(inputs="article",outputs="article")
    
    def __call__(self, request, context):
        context["article"]["html"] = slack2unicode(context["article"]["html"])
        context["article"]["title"] = slack2unicode(context["article"]["title"])
        try:
            context["title"] = slack2unicode(context["title"])
        except KeyError: pass

        return request, context

class ResolveLocalURLs(CheckedFilter):
    def __init__(self):
        super().__init__(inputs="article",outputs="article")
    
    def __call__(self, request, context):
        slug = context["article"]["slug"]
        html = context["article"]["html"]
        context["article"]["html"] = re.sub(s.BLOG_TEMPLATE_LOCAL_URL, slug, html)
        return request, context

def postprocessing():
    return SlackToUnicode() | ResolveLocalURLs()
