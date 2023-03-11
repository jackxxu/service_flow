from service_flow.middleware import Middleware, DecoratorMiddleware
from service_flow.flow import Flow
from service_flow.exceptions import ForkException
import pytest
import inspect

class InplaceModification2(Middleware):
    def __init__(self, increment):
        self.increment = increment

    async def __call__(self, bar: list):
        return await {'bar': [i + self.increment for i in bar]}


class AddContextVariable2(Middleware):
    async def __call__(self, foo, bar):
        return {'baz': 13}


class ReturnNone2(Middleware):
    async def __call__(self, baz):
        ...

class NestedService2(DecoratorMiddleware):
    async def __call__(self, context):
        try:
            return await self.app(context)
        except ZeroDivisionError:
            return {'error': 'decided by zero'}

@pytest.mark.asyncio
async def test_nested():
    flow = NestedService2() >> AddContextVariable2()
    assert type(flow) is Flow
    assert flow.async_mode == True
    assert await flow({'foo': 1, 'bar': 2}) == {'bar': 2, 'baz': 13, 'foo': 1}


@pytest.mark.asyncio
async def test_start_with_async():
    flow = AddContextVariable2() >> ReturnNone2()
    assert type(flow) is Flow
    assert flow.async_mode == True
    assert await flow({'foo': 1, 'bar': 2}) == {'foo': 1, 'bar': 2, 'baz': 13}


@pytest.mark.asyncio
async def test_multi_levels():
    flow = InplaceModification2(1) >>  \
            AddContextVariable2() >>  \
            ReturnNone2()

    assert type(flow) is Flow
    assert [type(m[0]) for m in flow.middlewares] == [
        InplaceModification2, AddContextVariable2, ReturnNone2
    ]

    assert [m[1] for m in flow.middlewares] == [
        ['bar'], ['foo', 'bar'], ['baz']
    ]

    assert flow.async_mode == True

    result = await flow({'foo': 'a', 'bar': [1, 2]})

    assert result == {
        'foo': 'a',
        'bar': [2, 3],
        'baz': 13
    }


class SetScenario(Middleware):
    def __call__(self, scenario: str):
        return {'scenario': scenario}

class OutputScenario(Middleware):
    def __call__(self, scenario):
        return {'scenario': scenario}

class InplaceModification2(Middleware):
    def __init__(self, increment):
        self.increment = increment

    def __call__(self, bar: list):
        return {'bar': [i + self.increment for i in bar]}


def test_fork3():
    flow = SetScenario() < \
            ('scenario', {
                'scenario1': InplaceModification2(1) >> OutputScenario(),
                'scenario2': InplaceModification2(2) >> OutputScenario(),
                })
    assert flow({'scenario': 'scenario1', 'foo': 1, 'bar': [1, 2]}) == {'scenario': 'scenario1', 'foo': 1, 'bar': [2, 3]}
    assert flow({'scenario': 'scenario2', 'foo': 2, 'bar': [1, 2]}) == {'scenario': 'scenario2', 'foo': 2, 'bar': [3, 4]}

    with pytest.raises(ForkException):
        assert flow({'scenario': 'scenario3', 'foo': 1, 'bar': [1, 2]})
