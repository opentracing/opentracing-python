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
