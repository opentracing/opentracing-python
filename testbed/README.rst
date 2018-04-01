Testbed suite for the OpenTracing API
=====================================

Testbed suite designed to test API changes.

Build and test.
---------------

.. code-block:: sh

    make testbed

Depending on whether Python 2 or 3 is being used, the ``asyncio`` tests will be automatically disabled.

Tested frameworks
-----------------

Currently the examples cover ``threading``, ``tornado``, ``gevent`` and ``asyncio`` (which requires Python 3). The implementation of ``ScopeManager`` for each framework is a basic, simple one, and can be found in `<span_propagation.py>`_. See details below.

threading
^^^^^^^^^

``ThreadScopeManager`` uses thread-local storage (through ``threading.local()``), and does not provide automatic propagation from thread to thread, which needs to be done manually.

gevent
^^^^^^

``GeventScopeManager`` uses greenlet-local storage (through ``gevent.local.local()``), and does not provide automatic propagation from parent greenlets to their children, which needs to be done manually.

tornado
^^^^^^^

``TornadoScopeManager`` uses a variation of ``tornado.stack_context.StackContext`` to both store **and** automatically propagate the context from parent coroutines to their children. 

Because of this, in order to make the ``TornadoScopeManager`` work, calls need to be started like this:

.. code-block:: python

    with tracer_stack_context():
        my_coroutine()

At the moment of writing this, yielding over multiple children is not supported, as the context is effectively shared, and switching from coroutine to coroutine messes up the current active ``Span``.

asyncio
^^^^^^^

``AsyncioScopeManager`` uses the current ``Task`` (through ``Task.current_task()``) to store the active ``Span``, and does not provide automatic propagation from parent ``Task`` to their children, which needs to be done manually.

List of patterns
----------------

- `Active Span replacement <test_active_span_replacement>`_ - Start an isolated task and query for its results in another task/thread.
- `Client-Server <test_client_server>`_ - Typical client-server example.
- `Common Request Handler <test_common_request_handler>`_ - One request handler for all requests.
- `Late Span finish <test_late_span_finish>`_ - Late parent ``Span`` finish.
- `Multiple callbacks <test_multiple_callbacks>`_ - Multiple callbacks spawned at the same time.
- `Nested callbacks <test_nested_callbacks>`_ - One callback at a time, defined ina pipeline fashion.
- `Subtask Span propagation <test_subtask_span_propagation>`_ - ``Span`` propagation for subtasks/coroutines.
