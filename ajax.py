from subprocess import CalledProcessError

from django.http import JsonResponse, Http404, HttpResponseServerError, HttpResponseBadRequest
from yaml import YAMLError

from . import article
from . import pandoc
from . import settings as s

def wip(request, slug):
    markdown_path = s.WIP_PATH / slug / s.MARKDOWN_FILENAME
    if not markdown_path.exists():
        raise Http404

    try: metadata = article.extract_metadata(markdown_path)
    except (YAMLError, IOError): metadata = {}

    try: html = pandoc.md2html(markdown_path)
    except FileNotFoundError as e: raise Http404
    except IOError as e: return HttpResponseServerError("IO Error")
    except ValueError as e: return HttpResponseServerError("Invalid request")
    except CalledProcessError as e:
        err_msg = "Error preparing file."
        if settings.DEBUG:
            err_msg += "\n" + e.cmd + "\n" + e.stderr
        return HttpResponseServerError(err_msg)

    html = article.post_processing(html, slug)
    context = { "html":html }
    context.update(metadata)

    return JsonResponse(context)
