import inspect
from types import LambdaType
from typing import Callable
import service_flow
from service_flow.fork import Fork
from service_flow.timer import measure_timing
import logging
logger = logging.getLogger(__name__)


class Flow():
    def __init__(self, m1: Callable):
        self.middlewares = []
        self.last_flow = self
        self.async_mode = False
        self._add_middleware(m1)

    @measure_timing
    def __call__(self, context: dict={}):
        return self.__run__(context) if self.async_mode == False else self.__async_run__(context)

    def __run__(self, context: dict):
        for middleware, kw_nms in self.middlewares:
            kwargs = self.middleware_kwargs(context, kw_nms)
            context_mods = middleware(**kwargs)
            context.update(context_mods if isinstance(context_mods, dict) else {})
        return context

    @staticmethod
    def middleware_kwargs(context: dict, kw_nms: list):
        if kw_nms == ['context']:  # context is a reserved argument keyword
            # if the middleware has a "context" parameter, then pass the entire context
            return {'context': context}
        else:
            # calls the middleware and get the result as modifications to the context
            return {key: context[key] for key in kw_nms if key in context}

    async def __async_run__(self, context: dict):
        for middleware, kw_nms in self.middlewares:
            kwargs = self.middleware_kwargs(context, kw_nms)
            # get the middleware output a la sync/async
            context_mods = await middleware(**kwargs) if middleware.is_async else middleware(**kwargs)
            context.update(context_mods if isinstance(context_mods, dict) else {})
        return context

    # handle >> operator for the sequential flow
    def __rshift__(self, middleware):
        # if the last middleware is a DecoratorMiddleware,
        # then it is a nested flow, and we need to add the new middleware to the nested flow
        if hasattr(self.last_middleware, 'app'):
            # for decorator pattern, the next middleware is added to the nested flow
            # so we are creating the new flow and keep its as an instance variable, and
            # next middleware will be added to this flow instead of the original one
            flow = Flow(middleware)
            self.last_middleware.app = flow
            self.last_flow = flow
        else:
            self.last_flow._add_middleware(middleware)

        # always return self, so that we can chain the >> operator
        return self

    @property
    def last_middleware(self):
        return self.last_flow.middlewares[-1][0]

    # handle < operator for the fork flow
    def __lt__(self, conditions: tuple):
        self.add_fork(conditions)
        return self

    def _add_middleware(self, middleware):
        # if middleware is an async function, then set the async_mode to True
        if isinstance(middleware, LambdaType):
            middleware = service_flow.middleware.LambdaMiddleware(middleware)

        if not self.async_mode and middleware.is_async:
            self.async_mode = True

        self.middlewares.append((middleware, Flow.arguments(middleware)))

    def add_fork(self, conditions: tuple):
        variable_nm = conditions[0]
        variable_conditions = conditions[1]
        fork = Fork(variable_nm, variable_conditions)
        self.middlewares.append((fork, fork.uniq_arguments))
        return self

    @staticmethod
    def arguments(middleware):
        return [x for x in inspect.signature(middleware).parameters.keys()]
