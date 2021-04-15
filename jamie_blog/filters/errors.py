from abc import ABC, abstractmethod

import django.http as http

class FilterError(Exception, ABC):
    def __init__(self, error_string : str):
        self.error_string = error_string

    @abstractmethod
    def handler(): pass


class ServerError(FilterError):
    def handler(self):
        return http.HttpResponseServerError(self, self.error_string)

class BadRequestError(FilterError):
    def handler(self):
        return http.HttpResponseBadRequest(self, self.error_string)

class NotFound(FilterError):
    def __init__(self): pass
    def handler(self):
        raise http.Http404
