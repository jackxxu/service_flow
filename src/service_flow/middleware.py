from service_flow.flow import Flow


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


class DecoratorMiddleware(Middleware):
    def __init__(self):
        self.next: Flow = None
