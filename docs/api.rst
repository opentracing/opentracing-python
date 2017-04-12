Python API
==========

Tracing
-------

Classes
^^^^^^^
.. autoclass:: opentracing.Tracer
   :members:

.. autoclass:: opentracing.ReferenceType
   :members:

.. autoclass:: opentracing.Reference
   :members:

Utility Functions
^^^^^^^^^^^^^^^^^
.. autofunction:: opentracing.start_child_span

.. autofunction:: opentracing.child_of

.. autofunction:: opentracing.follows_from

Spans
-----
.. autoclass:: opentracing.Span
   :members:

.. autoclass:: opentracing.SpanContext
   :members:

Propagation
-----------
.. autoclass:: opentracing.Format
   :members:

Exceptions
----------
.. autoclass:: opentracing.InvalidCarrierException
   :members:

.. autoclass:: opentracing.SpanContextCorruptedException
   :members:

.. autoclass:: opentracing.UnsupportedFormatException
   :members:
