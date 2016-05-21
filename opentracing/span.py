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

import re


class Span(object):
    """
    Span represents a unit of work executed on behalf of a trace. Examples of
    spans include a remote procedure call, or a in-process method call to a
    sub-component. A trace is required to have a single, top level "root"
    span, and zero or more children spans, which in turns can have their own
    children spans, thus forming a tree structure.

    Span implements a Context Manager API that allows the following usage:

    .. code-block:: python

        span = tracer.start_span(operation_name='go_fishing')
        with span:
            call_some_service()

    In this case it's not necessary to call span.finish()
    """

    def __init__(self, tracer):
        self._tracer = tracer

    def set_operation_name(self, operation_name):
        """Sets or changes the operation name.

        :param operation_name: the new operation name
        :return: Returns the Span itself, for call chaining.
        """
        return self

    def finish(self, finish_time=None):
        """Indicates that the work represented by this span has been completed
        or terminated, and is ready to be sent to the Reporter.

        If any tags / logs need to be added to the span, it should be done
        before calling finish(), otherwise they may be ignored.

        :param finish_time: an explicit Span finish timestamp as a unix
            timestamp per time.time()
        """
        pass

    def set_tag(self, key, value):
        """Attaches a key/value pair to the span.

        The set of supported value types is implementation specific. It is the
        responsibility of the actual tracing system to know how to serialize
        and record the values.

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

    def log_event(self, event, payload=None):
        """Logs an event against the span, with the current timestamp.

        :param event: an event name as a string
        :param payload: an arbitrary structured payload. Implementations may
            choose to ignore none, some, or all of the payload.
        :return: returns the span itself, for chaining the calls
        """
        return self

    def log(self, **kwargs):
        """Records a generic Log event at an arbitrary timestamp.

        :param timestamp: the log timestamp as a unix timestamp per time.time()
        :param event: an event name as a string
        :param payload: an arbitrary structured payload. Implementations may
            choose to ignore none, some, or all of the payload.
        :return: returns the span itself, for chaining the calls
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

        Note 3: keys are case-insensitive, to allow propagation via HTTP
        headers. Keys must match regexp `(?i:[a-z0-9][-a-z0-9]*)`. See
        `canonicalize_baggage_key()` for a way of checking and canonicalizing
        a key. If a key doesn't meet these guidelines, the behavior of
        `set_baggage_item()` will be undefined.

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

        Key is case-insensitive.

        :param key: key of the Baggage item
        :type key: str

        :rtype : str
        :return: value of the Baggage item with given key, or None.
        """
        return None

    @property
    def tracer(self):
        """Provides access to the Tracer that created this Span.

        :return: returns the Tracer that created this Span.
        """
        return self._tracer

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
            self.log_event('python.exception', {'type': exc_type,
                                                'val': exc_val,
                                                'tb': exc_tb})
        self.finish()


def start_child_span(parent_span, operation_name, tags=None, start_time=None):
    """A shorthand method that starts a child span given a parent span.

    Equivalent to calling

        parent_span.tracer().start_span(operation_name, parent_span, ...)

    :param parent_span: the Span which will act as the parent of the returned
        child Span instance
    :param operation_name: the operation name for the child Span instance
    :param tags: optional dict of Span Tags. The caller gives up ownership of
        that dict, because the Tracer may use it as-is to avoid extra data
        copying.
    :param start_time: an explicit Span start time as a unix timestamp per
        time.time().

    :return: Returns an already-started Span instance.
    """
    return parent_span.tracer.start_span(
        operation_name=operation_name,
        parent=parent_span,
        tags=tags,
        start_time=start_time
    )


_baggage_key_re = re.compile('^(?i)([a-z0-9][-a-z0-9]*)$')


def canonicalize_baggage_key(key):
    """canonicalize_baggage_key returns a canonicalized key if it's valid.

    :param key: a string that is expected to match the pattern specified by
        `get_baggage_item()`.

    :return: Returns the canonicalized key if it's valid, otherwise it returns
        None.
    """
    if _baggage_key_re.match(key) is not None:
        return key.lower()
    return None
