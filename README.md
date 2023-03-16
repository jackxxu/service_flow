# service-flow

<img src='https://www.worksmartsystems.com/images/C3_4StationL3.gif' width="35%" height="35%" align="right" />

A small, simple, and elegant component/function orchestration framework for Python, `service-flow` enables separation of a functionality into single-responsibility and bite-size functions/service objects, which are testable and reuseable. It further helps with readability and maintainability of the embedding application. It supports both sync and async services.

- [Implementation](#implementation)
  - [flow](#flow)
    - [basic example (`>>`)](#basic-example-)
    - [fork example (`<`)](#fork-example-)
  - [services](#services)
    - [example](#example)
      - [basic service](#basic-service)
      - [decorator service](#decorator-service)
    - [async service](#async-service)
    - [lambda service](#lambda-service)
    - [conventions](#conventions)
      - [initialization parameters](#initialization-parameters)
      - [function parameters](#function-parameters)
      - [return value](#return-value)
  - [exceptions](#exceptions)
- [inspiration](#inspiration)
- [TODOs](#todos)
- [install](#install)

## Implementation

`service-flow` has two parts -- a `flow` and multiple `services` (Note: the word `service` here refers to a function, not RESTful services):

### flow

a flow is the definition of processing procedure. It is defined as the following:

#### basic example (`>>`)

```python
flow = Service1() >> \
        Service2(*args) >> \
        ...
        ServiceN(**kwargs)

output = flow(input) ## input is a dictionary with all the input parameters as attributes
```

Python `>>` operator is overloaded to define the sequence of the processing. `Service1()`, ..., `ServiceN()` are instances of the services, or functions.

for each processing of the input, `service-flow` creates a **context**, a dictionary-like object that serves as input and gather outputs from all the services.


#### fork example (`<`)

```python
flow = Service1() >> \
        Service2(*args) < \
        ('context_var_name', {
            'var_value1': (Service3() >> Service4(**kwargs)),
            'var_value2': (Service5() >> Service4(**kwargs)),
          }
        )

output = flow(input) ## input is a dictionary with all the input parameters as attributes
```

Python `<` operator is overloaded to define a fork in processing. In this example, `context_var_name` is the name of context key, and `var_value1`, `var_value2` are potential values for forking.

A fork can not be the first service in a flow definition.

### services

A service is the equivalent of a Python function.

#### example

##### basic service

A element in a list of services that composes the flow. it inherits from `service_flow.middleware.Middleware`.


```python
class InplaceModification(Middleware):
    def __init__(self, increment): # initialization
        self.increment = 1

    def __call__(self, bar: list): # service call
        return {'bar': [i + self.increment for i in bar]}
```

##### decorator service

As the name implies, decorator service works similiarly to a python decorator that is nested on top of the subsequent flow.

A decorator service inherits from `service_flow.middleware.DecoratorMiddleware` and has one additional instance variable `app`, which is the reference to the subsequent flow.


```python
class ExceptionHandler(DecoratorMiddleware):
    def __call__(self, context):
        try:
            self.app(context)
        except ZeroDivisionError:
            return {'error': 'decided by zero'}
```


#### async service

As asyncio was introduced in python version 3.4, `service-flow` now supports async middlewares. here is example:

```python
import aiohttp

class GetPythonSiteHTML(Middleware):
    def __init__(self, increment):
        self.increment = increment

    async def __call__(self, bar: list):
      async with aiohttp.ClientSession() as session:
          async with session.get('http://python.org') as response:
              html = await response.text()
      return await {'response': html}
```

#### lambda service

`service-flow` supports simple functionality as a service in the form a lambda type. Note the following:

1. a lambda service is always sync
2. a lambda service can not be the first service on stack.

#### conventions

It needs to follow the convention below:

##### initialization parameters

parameters that initializes the service and is shared for all the calls to the service.

##### function parameters

These parameters are used as inputs to a service. They normally have to be existing attributes in the context object.

The only exception is if there is only one parameter and its name is "context", in which case the entire context dictionary will be passed in as the value of the context parameter.

##### return value

the return value of a service is optional. If a service does return values:

1. if it is a dictionary, it will add/update the aforementioned processing *context*.
2. otherwise, the return value is ignored and a warning message is logged.


### exceptions

`service-flow` raises a few types of exceptions:

1. `StopFlowException`: raised inside a service to signal stop processing. typical use cases include when incoming request is invalid.
2. `RetryException`: raised inside a service to signal re-processing of the same request. typical use cases include when a http request issued from the service times out or database transaction level violation.
3. `FatalException`: raised inside a service to restart the processor. typical use cases include when database connection is broken or other infrastructure related errors.


## inspiration

`service-flow` draws inspiration from the following Ruby projects:

1. [Rack](https://github.com/rack/rack)
2. [Light Service](https://github.com/adomokos/light-service)
3. [Ruby Middleware](https://github.com/Ibsciss/ruby-middleware)

## TODOs

## install

```cmd
pip install service-flow
```