Python API
==========

Classes
-------
.. autoclass:: opentracing.Span
   :members:

.. autoclass:: opentracing.SpanContext
   :members:

.. autoclass:: opentracing.Scope
   :members:

.. autoclass:: opentracing.ScopeManager
   :members:

.. autoclass:: opentracing.Tracer
   :members:

.. autoclass:: opentracing.ReferenceType
   :members:

.. autoclass:: opentracing.Reference
   :members:

.. autoclass:: opentracing.Format
   :members:

Utility Functions
-----------------
.. autofunction:: opentracing.start_child_span

.. autofunction:: opentracing.child_of

.. autofunction:: opentracing.follows_from

Exceptions
----------
.. autoclass:: opentracing.InvalidCarrierException
   :members:

.. autoclass:: opentracing.SpanContextCorruptedException
   :members:

.. autoclass:: opentracing.UnsupportedFormatException
   :members:

Scope managers
--------------
.. autoclass:: opentracing.ext.scope_manager.ThreadLocalScopeManager
   :members:

.. autoclass:: opentracing.ext.scope_manager.gevent.GeventScopeManager
   :members:

.. autoclass:: opentracing.ext.scope_manager.tornado.TornadoScopeManager
   :members:

.. autofunction:: opentracing.ext.scope_manager.tornado.tracer_stack_context

.. autoclass:: opentracing.ext.scope_manager.asyncio.AsyncioScopeManager
   :members:
