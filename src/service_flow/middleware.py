from service_flow import stack


class Middleware():

    def __rshift__(self, middleware):
        s = stack.Stack(self)
        s._add_middleware(middleware)
        return s

    def __call__(self):
        pass

    def __lt__(self, conditions: tuple):
        s = stack.Stack(self)
        s.add_fork(conditions)
        return s


