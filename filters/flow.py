import traceback

from .base import CheckedFilter
from .errors import FilterError


class For(CheckedFilter):
    def __init__(self, over: str, to: str, giving:str, result: str,
            f: CheckedFilter):
        super().__init__(inputs=over, outputs=to)
        # in = over, out = result
        self.f = f
        self.over = over
        self.giving = giving
        self.to = to
        self.result = result
        if f._in and to not in f._in:
            raise TypeError("For loop does not satisfy filter inputs:" +
                    str((f._in - {to})))

    def __call__(self, request, context):
        # TODO: consider changing the way this works
        context[self.result] = []

        for x in context[self.over]:
            temp_context = dict()
            temp_context.update(context)
            del temp_context[self.over]
            temp_context[self.to] = x
            result_request, result_context = self.f(request,temp_context)
            context[self.result].append(result_context[self.giving])

        try:
            temp_context
        except Exception:
            raise ValueError("No arguments for loop: {}".format(context[self.over]))

        return result_request, context

class Alternative(CheckedFilter):
    def __init__(self, left : CheckedFilter, right : CheckedFilter):
        self.left = left
        self.right = right
        self._in = left._in
        self._out = left._out

    def __call__(self, request, context):
        try:
            return self.left(request, context)
        except Exception as e:
            traceback.print_exc()
            print(e.args)
            if hasattr(e,"context"):
                context = e.context
            return self.right(request, context)

class Either(CheckedFilter):
    def __init__(self, f: CheckedFilter, error : FilterError):
        self.filter = f
        self.error = error
        self._in = f._in
        self._out = f._out

    def __call__(self, request, context):
        try:
            return self.filter(request, context)
        except Exception as e:
            raise self.error from e
