from service_flow.middleware import Middleware
from service_flow.stack import Stack
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
    stack = InplaceModification(1) >>  \
            AddContextVariable() >>  \
            ReturnNone()

    assert type(stack) is Stack
    assert [type(m[0]) for m in stack.middlewares] == [
        InplaceModification, AddContextVariable, ReturnNone
    ]

    assert [m[1] for m in stack.middlewares] == [
        ['bar'], ['foo', 'bar'], ['baz']
    ]

    assert stack({'foo': 'a', 'bar': [1, 2]}) == {
        'foo': 'a',
        'bar': [2, 3],
        'baz': 13
    }


def test_lambda():
    stack = InplaceModification(1) >>  \
            (lambda foo: {'return_value': foo})

    assert stack({'foo': 'a', 'bar': [1, 2]}) == {
        'foo': 'a', 
        'bar': [2, 3],
        'return_value': 'a'
    }

def test_fork3():
    stack = SetScenario() < \
            ('scenario', {
                'scenario1': (InplaceModification(1) >> AddContextVariable()),
                'scenario2': (InplaceModification(2) >> AddContextVariable()),
                })
    assert stack({'scenario': 'scenario1', 'foo': 1, 'bar': [1, 2]}) == {'scenario': 'scenario1', 'foo': 1, 'bar': [2, 3], 'baz': 13}
    assert stack({'scenario': 'scenario2', 'foo': 1, 'bar': [1, 2]}) == {'scenario': 'scenario2', 'foo': 1, 'bar': [3, 4], 'baz': 13}

    with pytest.raises(ForkException):   
        assert stack({'scenario': 'scenario3', 'foo': 1, 'bar': [1, 2]}) 

# def test_fork():
#     stack = SetScenario() < \
#             ('scenario', {
#                 'scenario1': lambda : {'results': '1'},
#                 'scenario2': lambda : {'results': '2'},
#                 })
#     assert stack({'scenario': 'scenario1'}) == {'results': '1', 'scenario': 'scenario1'}
#     assert stack({'scenario': 'scenario2'}) == {'results': '2', 'scenario': 'scenario2'}


# def test_fork2():
#     stack = SetScenario() >> \
#             (lambda scenario : {'value': scenario}) < \
#             ('scenario', {
#                 'scenario1': lambda : {'results': '1'},
#                 'scenario2': lambda : {'results': '2'},
#                 })
#     assert stack({'scenario': 'scenario1'}) == {'results': '1', 'scenario': 'scenario1', 'value': 'scenario1'}
#     assert stack({'scenario': 'scenario2'}) == {'results': '2', 'scenario': 'scenario2', 'value': 'scenario2'}
