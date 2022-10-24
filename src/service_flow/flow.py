import inspect
from types import LambdaType
from typing import Callable
from service_flow.fork import Fork
from service_flow.timer import measure_timing
import logging
logger = logging.getLogger(__name__)

class Flow():
    def __init__(self, m1: Callable):
        self.middlewares = []
        self.last_flow = self
        self._add_middleware(m1)

    @measure_timing
    def __call__(self, context: dict={}):
        for middleware, kw_nms in self.middlewares:
            # if the middleware has a "context" parameter, then pass the entire context
            if kw_nms == ['context']:
                context_mods = middleware(context)
            else:
                # for each middleware, get the arguments from the context
                kwargs = {key: context[key] for key in kw_nms if key in context}
                # calls the middleware and get the result as modifications to the context
                context_mods = middleware(**kwargs)
            if isinstance(context_mods, dict): # if the middleware returns a dict, update the context
                context.update(context_mods)
            elif context_mods == None: # if the middleware does not return anything, continue
                pass
            else: # if the middleware returns something else, raise an exception
                logger.warning(f"{type(middleware)}'s return value of type {type(context_mods)} is ignored in service-flow because it is not of type dict")

        return context

    # handle >> operator for the sequential flow
    def __rshift__(self, middleware):
        # if the last middleware is a DecoratorMiddleware,
        # then it is a nested flow, and we need to add the new middleware to the nested flow
        if hasattr(self.last_middleware, 'next'):
            # for decorator pattern, the next middleware is added to the nested flow
            # so we are creating the new flow and keep its as an instance variable, and 
            # next middleware will be added to this flow instead of the original one
            flow = Flow(middleware)
            self.last_middleware.next = flow
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
        self.middlewares.append((middleware, Flow.arguments(middleware)))

    def add_fork(self, conditions: tuple):
        variable_nm = conditions[0]
        variable_conditions = conditions[1]
        fork = Fork(variable_nm, variable_conditions)
        self.middlewares.append((fork, fork.uniq_arguments))
        return self

    @staticmethod
    def arguments(middleware):
        if isinstance(middleware, LambdaType):  # support for lambda func
            return inspect.getfullargspec(middleware).args
        else:  # Middleware object
            return inspect.getfullargspec(middleware.__call__).args[1:]
