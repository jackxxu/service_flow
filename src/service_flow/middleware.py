from service_flow.flow import Flow
import inspect
from functools import cached_property


class Middleware():
    # the following methods are only called on the first middleware,
    # either at the beginning of the flow or nested flow
    def __rshift__(self, middleware):
        s = Flow(self)
        s.__rshift__(middleware)
        return s

    def __lt__(self, conditions: tuple):
        s = Flow(self)
        s.add_fork(conditions)
        return s

    @cached_property
    def is_async(self):
        return inspect.iscoroutinefunction(self.__call__)

class DecoratorMiddleware(Middleware):
    def __init__(self):
        self.app: Flow = None
