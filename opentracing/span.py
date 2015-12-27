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


class Span(object):
    """
    Span represents a unit of work executed on behalf of a trace. Examples of
    spans include a remote procedure call, or a in-process method call to a
    sub-component. A trace is required to have a single, top level "root"
    span, and zero or more children spans, which in turns can have their own
    children spans, thus forming a tree structure.

    Span implements a Context Manager API that allows the following usage:

    .. code-block:: python

        span = tracer.start_trace(operation_name='go_fishing')
        with span:
            call_some_service()

    In this case it's not necessary to call span.finish()
    """

    def __init__(self, trace_context):
        self.trace_context = trace_context

    def __enter__(self):
        """Invoked when span is used as a context manager.

        Returns:
            itself
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ends context manager and calls finish() on the span.

        If exception has occurred during execution, it is automatically added
        as a tag to the span.
        """
        if exc_type:
            self.set_tag(str(exc_type), str(exc_val))
        self.finish()

    def start_child(self, operation_name):
        """Denotes the beginning of a subordinate unit of work.

        As this is a no-op implementation, it actually returns itself as the
        child span. Real implementations should create a new span.

        Args:
            operation_name: name of the new span from the perspective of the
                current service.

        Returns:
            A new child span in "started" state.
        """
        return self

    def finish(self):
        """Indicates that the work represented by this span has been completed
        or terminated, and is ready to be sent to the Reporter.

        If any tags / logs need to be added to the span, it should be done
        before calling finish(), otherwise they may be ignored.
        """
        pass

    def set_tag(self, key, value):
        """Attaches a key/value pair so the span.

        The set of supported value types is implementation specific. It is the
        responsibility of the actual tracing system to know how to serialize
        and record the values.

        :param key: key or name of the tag. Must be a string.
        :param value: value of the tag. Multi-valued tags are not supported

        :return: itself, for chaining
        :rtype: Span
        """
        return self

    def info(self, message, *args):
        """Logs an event/message against the span, with the current timestamp.

        :param message: a format string that can refer to fields
            in the args payload.
        :param args: arbitrary payload
        :return: returns the span itself, for chaining the calls
        """
        return self

    def error(self, message, *args):
        """Same as info(), but for errors.

        :param message: a format string that can refer to fields
            in the args payload.
        :param args: arbitrary payload
        :return: returns the span itself, for chaining the calls
        """
        return self
