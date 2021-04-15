from django.http import JsonResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render

from .base import CheckedFilter

class Render(CheckedFilter):
    def __init__(self, template, inputs={}):
        super().__init__(inputs=inputs)
        self.template = template

    def __call__(self, request, context):
        return render(request, self.template, context)

class JSON(CheckedFilter):
    def __init__(self, inputs={}):
        super().__init__(inputs=inputs)

    def __call__(self, request, context):
        return JsonResponse(context)

class ToRequestContext(CheckedFilter):
    def __call__(self, request, context):
        return RequestContext(request, context)

class Redirect(CheckedFilter):
    def __init__(self, url):
        super().__init__()
        self.url = url
    def __call__(self, request, context):
        return HttpResponseRedirect(self.url)
