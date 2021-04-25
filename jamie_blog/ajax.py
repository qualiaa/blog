import logging

from django.conf import settings as s
from django.http import HttpResponseNotModified

from .pipes import article as a
from .pipes import errors as e
from .pipes import cache as c
from .pipes.flow import Either, Alternative
from .pipes.inputs import ContextInput
from .pipes.outputs import JSON
from .pipes.postprocessing import postprocessing
from .pipes.utils import Extract, Remove


def wip(request, slug):
    path = s.BLOG_WIP_PATH / slug
    markdown_path = path / s.BLOG_MARKDOWN_FILENAME
    local_mtime = markdown_path.stat().st_mtime
    logging.debug("Server mtime: %s", local_mtime)
    if "mtime" in request.POST:
        logging.debug("Client mtime: %s", request.POST["mtime"])
        if int(local_mtime) <= float(request.POST["mtime"]):
            return HttpResponseNotModified()

    return ContextInput(request, path=path, slug=slug, mtime=local_mtime) >\
        a.MetadataSafe() |\
        Alternative(c.CachedText(),
                    Either(a.MetadataDangerous() | a.GetFullText() |
                           postprocessing() | c.CacheHTML(),
                           e.NotFound)) |\
        Extract("article") |\
        Remove({"path", "markdown"}) |\
        JSON()
