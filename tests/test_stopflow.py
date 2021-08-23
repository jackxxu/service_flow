from service_flow.middleware import Middleware
from service_flow.stack import Stack
from service_flow.exceptions import StopFlowException


class StopFlow(Middleware):
    def __call__(self):
        raise StopFlowException('some error message')


def test_stopflow():
    stack = StopFlow() >>  \
            (lambda foo: {'return_value': foo})

    assert stack({}) == {}
