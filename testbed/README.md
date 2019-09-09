# Testbed suite for the OpenTracing API

Testbed suite designed to test API changes.

## Build and test.

```sh
make testbed
```

Depending on whether Python 2 or 3 is being used, the `asyncio` tests will be automatically disabled.

Alternatively, due to the organization of the suite, it's possible to run directly the tests using `py.test`:

```sh
    py.test -s testbed/test_multiple_callbacks/test_threads.py
```

## Tested frameworks

Currently the examples cover `threading`, `tornado`, `gevent`, `asyncio` (which requires Python 3) and `contextvars` (which requires Python 3.7 and higher). Each example uses their respective `ScopeManager` instance from `opentracing.scope_managers`, along with their related requirements and limitations.

### threading, asyncio and gevent

No automatic `Span` propagation between parent and children tasks is provided, and thus the `Span` need to be manually passed down the chain.

### tornado

`TornadoScopeManager` uses a variation of `tornado.stack_context.StackContext` to both store **and** automatically propagate the context from parent coroutines to their children. 

Currently, yielding over multiple children is not supported, as the context is effectively shared, and switching from coroutine to coroutine messes up the current active `Span`.

### contextvars

`ContextVarsScopeManager` uses [contextvars](https://docs.python.org/3/library/contextvars.html) module to both store **and** automatically propagate the context from parent coroutines / tasks / scheduled in event loop callbacks to their children.

## List of patterns

- [Active Span replacement](test_active_span_replacement) - Start an isolated task and query for its results in another task/thread.
- [Client-Server](test_client_server) - Typical client-server example.
- [Common Request Handler](test_common_request_handler) - One request handler for all requests.
- [Late Span finish](test_late_span_finish) - Late parent `Span` finish.
- [Multiple callbacks](test_multiple_callbacks) - Multiple callbacks spawned at the same time.
- [Nested callbacks](test_nested_callbacks) - One callback at a time, defined ina pipeline fashion.
- [Subtask Span propagation](test_subtask_span_propagation) - `Span` propagation for subtasks/coroutines.

## Adding new patterns

A new pattern is composed of a directory under *testbed* with the *test_* prefix, and containing the files for each platform, also with the *test_* prefix:

```
testbed/
  test_new_pattern/
    test_threads.py
    test_tornado.py
    test_asyncio.py
    test_gevent.py
```

Supporting all the platforms is optional, and a warning will be displayed when doing `make testbed` in such case.
