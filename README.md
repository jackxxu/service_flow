# service-flow 

<img src='https://www.worksmartsystems.com/images/C3_4StationL3.gif' width="15%" height="15%" align="right" />

A small, simple, and elegant component/function orchestration framework for Python, `service-flow` enables separation of a functionality into single-responsibility and bite-size functions/service objects, which are testable and reuseable. It further helps with readability and maintainability of the embedding application.

- [Implementation](#implementation)
  - [flow](#flow)
    - [example](#example)
  - [services](#services)
    - [example](#example-1)
    - [conventions](#conventions)
      - [initializaition parameters](#initializaition-parameters)
      - [function parameters](#function-parameters)
      - [return value](#return-value)
- [inspiration](#inspiration)
- [TODOs](#todos)
- [install](#install)

## Implementation

`service-flow` has two parts -- a `flow` and multiple `services` (Note: the word `service` here refers to a function, not RESTful services):

### flow

a flow is the definition of processing procedure. It is defined as the following:

#### example

``` python
stack = Service1() >> \ 
        Service2(*args) >> \ 
        ... 
        ServiceN() 
        
output = stack(input) ## input is a dictionary with all the input parameters as attributes
```

Python `>>` operator is overloaded to define the sequeunce of the processing. `Service1()`, ..., `ServiceN()` are instances of the services, or functions.

for each processing of the input, `service-flow` creates a **context**, a dictionary-like object that serves as input and gather outputs from all the services.

### services

A service is the equivalent of a Python function. 

#### example

```python
class InplaceModification(Middleware):
    def __init__(self, increment): # initialization
        self.increment = 1

    def __call__(self, bar: list): # service call 
        return {'bar': [i + self.increment for i in bar]}
```

#### conventions

It needs to follow the convention below:

##### initializaition parameters
 
parameters that initializes the service and is shared for all the calls to the service.

##### function parameters

these are used to call a service and have to be existing attributes in the context object.

##### return value

the return value of a service is optional. If a service does return values:

1. if it is a dictionary, it will add/update the aforementioned processing *context*.
2. otherwise, the return value is ignored and a warning message is logged.


## inspiration

`service-flow` draws inspiration from the following Ruby projects:
 
1. [Light Service](https://github.com/adomokos/light-service)
2. [Ruby Middleware](https://github.com/Ibsciss/ruby-middleware)

## TODOs

1. implement forking


## install

```cmd
pip install service-flow
```