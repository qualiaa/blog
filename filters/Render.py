from .Filter import Filter
from django.shortcuts import render

class Render(Filter):
    def __init__(self, template):
        self.template = template

    def __call__(self, request, context):
        return render(request, self.template, context)
