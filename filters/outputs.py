from django.shortcuts import render

from .base import CheckedFilter

class Render(CheckedFilter):
    def __init__(self, template, inputs={}):
        super().__init__(inputs=inputs)
        self.template = template

    def __call__(self, request, context):
        return render(request, self.template, context)
