import logging
import traceback

from .base import CheckedPipe
from .errors import PipeError


class For(CheckedPipe):
    def __init__(self, over: str, to: str, giving:str, result: str,
                 f: CheckedPipe):
        super().__init__(inputs=over, outputs=to)
        # in = over, out = result
        self.f = f
        self.over = over
        self.giving = giving
        self.to = to
        self.result = result
        if f._in and to not in f._in:
            raise TypeError("For loop does not satisfy pipe inputs:" +
                            str((f._in - {to})))

    def __call__(self, request, context):
        # TODO: consider changing the way this works
        context[self.result] = []

        for x in context[self.over]:
            temp_context = dict()
            temp_context.update(context)
            del temp_context[self.over]
            temp_context[self.to] = x
            result_request, result_context = self.f(request, temp_context)
            context[self.result].append(result_context[self.giving])

        try:
            temp_context
        except Exception as e:
            raise ValueError(
                f"No arguments for loop: {context[self.over]}") from e

        return result_request, context


class Alternative(CheckedPipe):
    def __init__(self, left: CheckedPipe, right: CheckedPipe):
        self.left = left
        self.right = right
        self._in = left._in
        self._out = left._out

    def __call__(self, request, context):
        try:
            return self.left(request, context)
        except Exception as e:
            logging.warning("Alternative received exception")
            logging.warning("%s%s", type(e), e.args)
            logging.debug("%s", traceback.format_exc())
            if hasattr(e, "context"):
                context = e.context
            return self.right(request, context)


class Either(CheckedPipe):
    def __init__(self, f: CheckedPipe, error: PipeError):
        self.pipe = f
        self.error = error
        self._in = f._in
        self._out = f._out

    def __call__(self, request, context):
        try:
            return self.pipe(request, context)
        except PipeError as e:
            raise self.error from e
