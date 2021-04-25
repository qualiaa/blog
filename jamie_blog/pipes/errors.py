from abc import ABC, abstractmethod

import django.http as http

class PipeError(Exception, ABC):
    def __init__(self, error_string: str, *args, **kargs):
        self.error_string = error_string
        Exception.__init__(self, error_string, *args, **kargs)

    @abstractmethod
    def handler(): pass

class ServerError(PipeError):
    def handler(self):
        return http.HttpResponseServerError(self, self.error_string)


class BadRequestError(PipeError):
    def handler(self):
        return http.HttpResponseBadRequest(self, self.error_string)


class NotFound(PipeError):
    def handler(self):
        raise http.Http404
