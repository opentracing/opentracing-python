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
from concurrent.futures import Future
from .span import Span
from .context import TraceContextSource
from .context import TraceContextMarshaler, TraceContextUnmarshaler


class Tracer(TraceContextMarshaler, TraceContextUnmarshaler, object):
    """Tracer is the entry point API between instrumentation code and the
    tracing implementation.

    This implementation both defines the public Tracer API, and provides
    a default no-op behavior.
    """

    singleton_noop_span = Span(TraceContextSource.singleton_noop_trace_context)

    def start_trace(self, operation_name):
        """Starts a new trace and creates a new root span.

        This method should be used by services that are instrumented for
        tracing but did not receive trace ID from upstream request.

        :param operation_name: the service's own name for the end-point
            that received the request represented by this trace and span.
            The domain of names must be limited, e.g. do not use UUIDs or
            entity IDs or timestamps as part of the name.

        :return: a new root Span
        """
        return Tracer.singleton_noop_span

    def join_trace(self, operation_name, parent_trace_context):
        """Joins a trace started elsewhere and creates a new span as a
        child of the given parent trace context.

        This method should be used by services that receive tracing info
        from upstream.

        :param operation_name: the service's own name for the end-point
            that received the request represented by this trace and span.
            The domain of names must be limited, e.g. do not use UUIDs or
            entity IDs or timestamps as part of the name.
        :param parent_trace_context: Trace Context of a client span started
            elsewhere and whose trace we're joining.

        :return: a new Span
        """
        return Tracer.singleton_noop_span

    def close(self):
        """Performs a clean shutdown of the tracer, flushing any traces that
        may have been buffered in memory.

        :return: Returns a :py:class:futures.Future
        """
        fut = Future()
        fut.set_result(True)
        return fut
