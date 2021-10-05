import inspect
from types import LambdaType
from service_flow.exceptions import StopFlowException, ForkException
from service_flow.timer import measure_timing
import logging
import itertools

logger = logging.getLogger(__name__)

class Fork():
    def __init__(self, fork_var: str, fork_conditions: dict):
        self.fork_var = fork_var
        self.fork_conditions = fork_conditions

    def __call__(self, **context):
        value = context[self.fork_var]
        try:
            func = self.fork_conditions[value]
        except KeyError as e:
            raise ForkException(f'value {value} does not match any fork key') from e
        return func(context)

    @property
    def uniq_arguments(self):
        list2d = [middleware[1] for _, stack in self.fork_conditions.items() for middleware in stack.middlewares]
        list2d.append([self.fork_var])
        return list(set(itertools.chain(*list2d)))


class Stack():
    def __init__(self, m1):
        self.middlewares = []
        self._add_middleware(m1)
    
    @measure_timing
    def __call__(self, context: dict={}):
        try:
            for middleware, kw_nms in self.middlewares:
                kwargs = {key: context[key] for key in kw_nms if key in context}
                context_mods = middleware(**kwargs)
                if isinstance(context_mods, dict):
                    context.update(context_mods)
                elif context_mods != None:
                    logger.warning(f"{type(middleware)}'s return value of type {type(context_mods)} is ignored in service-flow because it is not of type dict")
        except StopFlowException as sfe:
            logger.warning(f'stop processing all the middlewares due to StopFlowException {sfe}')
        except ForkException as fe:
            logger.exception(f'stop processing all the middlewares due to StopFlowException {fe}')

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
        self.middlewares.append((fork, fork.uniq_arguments))
        return self

    @staticmethod
    def arguments(middleware):
        if isinstance(middleware, LambdaType):  # support for lambda func
            return inspect.getfullargspec(middleware).args
        else:  # Middleware object
            return inspect.getfullargspec(middleware.__call__).args[1:]
