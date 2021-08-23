import inspect
from types import LambdaType
from service_flow.exceptions import StopFlowException
import logging

logger = logging.getLogger(__name__)

class Fork():
    def __init__(self, fork_var: str, fork_conditions: dict):
        self.fork_var = fork_var
        self.fork_conditions = fork_conditions

    def __call__(self, **kwargs):
        value = kwargs[self.fork_var]
        func = self.fork_conditions[value]
        return func()


class Stack():
    def __init__(self, m1):
        self.middlewares = []
        self._add_middleware(m1)

    def __call__(self, context: dict):
        for middleware, kw_nms in self.middlewares:
            kwargs = {key: context[key] for key in kw_nms}
            try:
                context_mods = middleware(**kwargs)
            except StopFlowException as sfe:
                logger.warn(f'stop processing all the middlewares due to StopFlowException {sfe}')
                break

            if type(context_mods) == dict:
                context.update(context_mods)
        return context

    def __rshift__(self, middleware):
        self._add_middleware(middleware)
        return self

    def __lt__(self, conditions: tuple):
        self.add_fork(conditions)
        return self

    def _add_middleware(self, middleware):
        self.middlewares.append((middleware, Stack.arguments(middleware)))

    def add_fork(self, conditions: tuple):
        variable_nm = conditions[0]
        variable_conditions = conditions[1]
        fork = Fork(variable_nm, variable_conditions)
        self.middlewares.append((fork, [variable_nm]))
        return self

    @staticmethod
    def arguments(middleware):
        if isinstance(middleware, LambdaType):  # support for lambda func
            return inspect.getfullargspec(middleware).args
        else:  # Middleware object
            return inspect.getfullargspec(middleware.__call__).args[1:]
