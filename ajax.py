from django.http import HttpResponseNotModified

from .filters import article as a
from .filters import errors as e
from .filters.flow import Either
from .filters.inputs import ContextInput
from .filters.outputs import JSON, ToRequestContext
from .filters.postprocessing import postprocessing
from .filters.utils import Extract, Remove

from . import settings as s

def wip(request, slug):
    path = s.WIP_PATH / slug 
    markdown_path = path / s.MARKDOWN_FILENAME
    local_mtime = markdown_path.stat().st_mtime 
    if "mtime" in request.POST:
        if int(local_mtime) <= float(request.POST["mtime"]):
            return HttpResponseNotModified()

    return ContextInput(request, path=path, slug=slug, mtime=local_mtime) >\
            a.MetadataSafe()   |\
            Either(a.MetadataDangerous() | a.GetFullText() | postprocessing(),
                   e.NotFound) |\
            Extract("article")  |\
            Remove({"path","markdown"}) |\
            JSON()
