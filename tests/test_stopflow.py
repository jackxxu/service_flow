from service_flow.middleware import Middleware
from service_flow.exceptions import StopFlowException
import pytest

class StopFlow(Middleware):
    def __call__(self):
        raise StopFlowException('some error message')


def test_stopflow():
    flow = StopFlow() >>  \
            (lambda foo: {'return_value': foo})
    with pytest.raises(StopFlowException):
        flow({})
