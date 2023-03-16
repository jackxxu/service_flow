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

class LambdaMiddleware(Middleware):
    def __init__(self, func):
        self.func = func
        # set the function signature to the middleware
        self.__signature__ = inspect.signature(func)

    @cached_property
    def is_async(self):
        return False  # lambda is always sync

    def __call__(self, **kwargs):
        return self.func(**kwargs)

class DecoratorMiddleware(Middleware):
    def __init__(self):
        self.app: Flow = None
