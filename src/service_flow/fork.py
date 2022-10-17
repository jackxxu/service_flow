import itertools
from service_flow.exceptions import ForkException


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
        list2d = [middleware[1] for _, flow in self.fork_conditions.items() for middleware in flow.middlewares]
        list2d.append([self.fork_var])
        return list(set(itertools.chain(*list2d)))
