from service_flow.middleware import Middleware, DecoratorMiddleware
from service_flow.flow import Flow
from service_flow.exceptions import ForkException
import pytest


class InplaceModification(Middleware):
    def __init__(self, increment):
        self.increment = increment

    def __call__(self, bar: list):
        return {'bar': [i + self.increment for i in bar]}


class AddContextVariable(Middleware):
    def __call__(self, foo, bar):
        return {'baz': 13}


class ReturnNone(Middleware):
    def __call__(self, baz):
        ...


class SetScenario(Middleware):
    def __call__(self, scenario: str):
        return {'scenario': scenario}


def test_multi_levels():
    flow = InplaceModification(1) >>  \
            AddContextVariable() >>  \
            ReturnNone()

    assert type(flow) is Flow
    assert [type(m[0]) for m in flow.middlewares] == [
        InplaceModification, AddContextVariable, ReturnNone
    ]

    assert [m[1] for m in flow.middlewares] == [
        ['bar'], ['foo', 'bar'], ['baz']
    ]

    assert flow({'foo': 'a', 'bar': [1, 2]}) == {
        'foo': 'a',
        'bar': [2, 3],
        'baz': 13
    }


def test_lambda():
    flow = InplaceModification(1) >>  \
            (lambda foo: {'return_value': foo})

    assert flow({'foo': 'a', 'bar': [1, 2]}) == {
        'foo': 'a',
        'bar': [2, 3],
        'return_value': 'a'
    }

def test_fork3():
    flow = SetScenario() < \
            ('scenario', {
                'scenario1': InplaceModification(1) >> AddContextVariable(),
                'scenario2': InplaceModification(2) >> AddContextVariable(),
                })
    assert flow({'scenario': 'scenario1', 'foo': 1, 'bar': [1, 2]}) == {'scenario': 'scenario1', 'foo': 1, 'bar': [2, 3], 'baz': 13}
    assert flow({'scenario': 'scenario2', 'foo': 1, 'bar': [1, 2]}) == {'scenario': 'scenario2', 'foo': 1, 'bar': [3, 4], 'baz': 13}

    with pytest.raises(ForkException):
        assert flow({'scenario': 'scenario3', 'foo': 1, 'bar': [1, 2]})

class NestedService(DecoratorMiddleware):
    def __call__(self, context):
        try:
            self.app(context)
        except ZeroDivisionError:
            return {'error': 'decided by zero'}

class CustomException(Exception):
    pass

def test_nested():
    flow = InplaceModification(1) >>  \
            NestedService() >>  \
            (lambda foo: {'result': 1/foo})
    assert flow({'foo': 0, 'bar': []}) == {
        'bar': [],
        'error': 'decided by zero',
        'foo': 0
    }

    assert flow({'foo': 1, 'bar': []}) == {
        'bar': [],
        'foo': 1,
        'result': 1
    }

    flow = NestedService() >>  \
            (lambda foo: {'result': 1/foo})
    assert flow({'foo': 0, 'bar': []}) == {
        'bar': [],
        'error': 'decided by zero',
        'foo': 0
    }

    flow = NestedService() >> (lambda foo: {'result1': 1/foo}) >> (lambda bar: {'result2': 2/bar})
    assert flow({'foo': 1, 'bar': 2}) == {
        'bar': 2,
        'foo': 1,
        'result1': 1,
        'result2': 1
    }

    class DoNothing(Middleware):
        def __call__(self):
            return {}

    flow = DoNothing() >> NestedService() >> (lambda foo: {'result1': 1/foo}) >> (lambda bar: {'result2': 2/bar})
    assert flow({'foo': 1, 'bar': 2}) == {
        'bar': 2,
        'foo': 1,
        'result1': 1,
        'result2': 1
    }