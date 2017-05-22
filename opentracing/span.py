# Copyright (c) 2016 The OpenTracing Authors.
#
# Copyright (c) 2015 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import


class SpanContext(object):
    """SpanContext represents Span state that must propagate to descendant
    Spans and across process boundaries.

    SpanContext is logically divided into two pieces: the user-level "Baggage"
    (see set_baggage_item and get_baggage_item) that propagates across Span
    boundaries and any Tracer-implementation-specific fields that are needed to
    identify or otherwise contextualize the associated Span instance (e.g., a
    <trace_id, span_id, sampled> tuple).
    """

    EMPTY_BAGGAGE = {}  # TODO would be nice to make this immutable

    @property
    def baggage(self):
        """
        Return baggage associated with this SpanContext.
        If no baggage has been added to the span, returns an empty dict.

        The caller must not modify the returned dictionary.

        See also: Span.set_baggage_item() / Span.get_baggage_item()

        :rtype: dict
        :return: returns baggage associated with this SpanContext or {}.
        """
        return SpanContext.EMPTY_BAGGAGE


class BaseSpan(object):
    """
    BaseSpan represents the OpenTracing specification's span contract,
    which is a unit of work executed on behalf of a trace. Examples of
    spans include a remote procedure call, or a in-process method call to a
    sub-component. Every span in a trace may have zero or more causal parents,
    and these relationships transitively form a DAG. It is common for spans to
    have at most one parent, and thus most traces are merely tree structures.
    """

    @property
    def context(self):
        """Provides access to the SpanContext associated with this Span.

        The SpanContext contains state that propagates from Span to Span in a
        larger trace.

        :return: returns the SpanContext associated with this Span.
        """
        return None

    def set_operation_name(self, operation_name):
        """Changes the operation name.

        :param operation_name: the new operation name
        :return: Returns the Span itself, for call chaining.
        """
        return self

    def set_tag(self, key, value):
        """Attaches a key/value pair to the span.

        The value must be a string, a bool, or a numeric type.

        If the user calls set_tag multiple times for the same key,
        the behavior of the tracer is undefined, i.e. it is implementation
        specific whether the tracer will retain the first value, or the last
        value, or pick one randomly, or even keep all of them.

        :param key: key or name of the tag. Must be a string.
        :param value: value of the tag.

        :return: Returns the Span itself, for call chaining.
        :rtype: Span
        """
        return self

    def log_kv(self, key_values, timestamp=None):
        """Adds a log record to the Span.

        For example::

            span.log_kv({
                "event": "time to first byte",
                "packet.size": packet.size()})

            span.log_kv({"event": "two minutes ago"}, time.time() - 120)

        :param key_values: A dict of string keys and values of any type
        :type key_values: dict

        :param timestamp: A unix timestamp per time.time(); current time if
            None
        :type timestamp: float

        :return: Returns the Span itself, for call chaining.
        :rtype: Span
        """
        return self

    def set_baggage_item(self, key, value):
        """Stores a Baggage item in the span as a key/value pair.

        Enables powerful distributed context propagation functionality where
        arbitrary application data can be carried along the full path of
        request execution throughout the system.

        Note 1: Baggage is only propagated to the future (recursive) children
        of this Span.

        Note 2: Baggage is sent in-band with every subsequent local and remote
        calls, so this feature must be used with care.

        :param key: Baggage item key
        :type key: str

        :param value: Baggage item value
        :type value: str

        :rtype : Span
        :return: itself, for chaining the calls.
        """
        return self

    def get_baggage_item(self, key):
        """Retrieves value of the Baggage item with the given key.

        :param key: key of the Baggage item
        :type key: str

        :rtype : str
        :return: value of the Baggage item with given key, or None.
        """
        return None

    def log_event(self, event, payload=None):
        """DEPRECATED"""
        if payload is None:
            return self.log_kv({'event': event})
        else:
            return self.log_kv({'event': event, 'payload': payload})

    def log(self, **kwargs):
        """DEPRECATED"""
        key_values = {}
        if 'event' in kwargs:
            key_values['event'] = kwargs['event']
        if 'payload' in kwargs:
            key_values['payload'] = kwargs['payload']
        timestamp = None
        if 'timestamp' in kwargs:
            timestamp = kwargs['timestamp']
        return self.log_kv(key_values, timestamp)


class Span(BaseSpan):
    """Span represents a OpenTracing span's implementation, which is
    *manually propagated* within the given process. Most of this API
    lives in BaseSpan.

    Span implements a Context Manager API that allows the following usage:

    .. code-block:: python

        with tracer.start_span(operation_name='go_fishing') as span:
            call_some_service()

    In the Context Manager syntax it's not necessary to call span.finish()
    """
    def __init__(self, tracer, context):
        self._tracer = tracer
        self._context = context

    @property
    def context(self):
        """Provides access to the SpanContext associated with this Span.

        :return: returns the SpanContext associated with this Span.
        """
        return self._context

    @property
    def tracer(self):
        """Provides access to the Tracer that created this Span.

        :return: returns the Tracer that created this Span.
        """
        return self._tracer

    def finish(self, finish_time=None):
        """Indicates that the work represented by this span has completed or
        terminated.

        With the exception of the `Span.context` property, the semantics of all
        other Span methods are undefined after `finish()` has been invoked.

        :param finish_time: an explicit Span finish timestamp as a unix
            timestamp per time.time()
        """
        pass

    def __enter__(self):
        """Invoked when span is used as a context manager.

        :return: returns the Span itself
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ends context manager and calls finish() on the span.

        If exception has occurred during execution, it is automatically added
        as a tag to the span.
        """
        if exc_type:
            self.log_kv({
                'python.exception.type': exc_type,
                'python.exception.val': exc_val,
                'python.exception.tb': exc_tb,
                })
        self.finish()


class ActiveSpan(BaseSpan):
    """ActiveSpan represents a OpenTracing span's implementation,
    wrapping a Span object, layering on in-process propagation capabilities.

    In any given thread there is at most one active span primarily
    responsible for the work accomplished by the surrounding application code.
    The ActiveSpan may be accessed via the ActiveSpanSource.active_span
    property. If the application needs to defer work that should be part of
    the same Span, the Source provides a ActiveSpan.capture() method that
    returns an ActiveSpanContinuation; this continuation may be used to
    re-activate and continue the Span in that other thread.

    ActiveSpan implements a Context Manager API that allows the following
    usage:

    .. code-block:: python

        with tracer.start_active_span(operation_name='go_fishing') as span:
            call_some_service()

    In the Context Manager syntax it's not necessary to call span.deactivate()
    """

    def __init__(self, wrapped):
        self._wrapped = wrapped
        self._noop_continuation = ActiveSpanContinuation()

    def deactivate(self):
        """Mark the end of the active period for the current thread and
        ActiveSpan. When the last ActiveSpan is deactivated for a given Span,
        it is automatically finished with a call to Span.finish().
        """
        pass

    def capture(self):
        """Capture a new ActiveSpanContinuation associated with this
        ActiveSpan and Span. The ActiveSpanContinuation may be used as data
        in a closure or callback function where the ActiveSpan may be resumed
        and reactivated.

        IMPORTANT: the caller MUST call ActiveSpanContinuation.activate() and
        call ActiveSpan.deactivate() or the associated Span will never be
        finished. That is, calling capture() increments a refcount that must be
        decremented somewhere else.
        """
        return self._noop_continuation

    @property
    def wrapped(self):
        """Provides access to the wrapped Span this active
        object holds.

        :return: returns the wrapped Span.
        """
        return self._wrapped

    @property
    def context(self):
        """Provides access to the wrapped Span's context.

        :return: returns the wrapped Span's context.
        """
        return self._wrapped.context

    def set_operation_name(self, operation_name):
        """Changes the operation name of the wrapped Span.

        :param operation_name: the new operation name
        :return: Returns the ActiveSpan itself, for call chaining.
        """
        self._wrapped.set_operation_name(operation_name)
        return self

    def set_tag(self, key, value):
        """Attaches a key/value pair to the wrapped Span.

        :return: Returns the ActiveSpan itself, for call chaining.
        :rtype: ActiveSpan
        """
        self._wrapped.set_tag(key, value)
        return self

    def log_kv(self, key_values, timestamp=None):
        """Adds a log record to the wrapped Span.

        :param key_values: A dict of string keys and values of any type
        :type key_values: dict

        :param timestamp: A unix timestamp per time.time(); current time if
            None
        :type timestamp: float

        :return: Returns the ActiveSpan itself, for call chaining.
        :rtype: ActiveSpan
        """
        self._wrapped.log_kv(key_values, timestamp)
        return self

    def set_baggage_item(self, key, value):
        """Stores a Baggage item in the wrapped Span as a key/value pair.

        :param key: Baggage item key
        :type key: str

        :param value: Baggage item value
        :type value: str

        :rtype : ActiveSpan
        :return: itself, for chaining the calls.
        """
        self._wrapped.set_baggage_item(key, value)
        return self

    def get_baggage_item(self, key):
        """Retrieves value of the Baggage item with the given key
        for the wrapped Span.

        :param key: key of the Baggage item
        :type key: str

        :rtype : str
        :return: value of the Baggage item with given key, or None.
        """
        return self._wrapped.get_baggage_item(key)

    def __enter__(self):
        """Invoked when the span is used as a context manager.

        :return: returns the ActiveSpan itself
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ends context manager and calls deactive() on the active span.

        If exception has occurred during execution, it is automatically added
        as a tag to the wrapped span.
        """
        if exc_type:
            self.log_kv({
                'python.exception.type': exc_type,
                'python.exception.val': exc_val,
                'python.exception.tb': exc_tb,
                })
        self.deactivate()


class ActiveSpanContinuation(object):
    """An ActiveSpanContinuation can be used *once* to activate a Span, then
    deactivate when processing activity moves on to another Span
    (in practice, this active period typically extends for the length
    of a deferred async closure invocation).
    """

    def activate(self):
        """Make the Span encapsulated by this ActiveSpanContinuation
        active and return it.

        :rtype : ActiveSpan
        :return: The newly-activated ActiveSpan.
        """
        return ActiveSpan(BaseSpan())
