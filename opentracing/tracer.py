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
from .propagator import SpanPropagator


class Tracer(SpanPropagator):
    """Tracer is the entry point API between instrumentation code and the
    tracing implementation.

    This implementation both defines the public Tracer API, and provides
    a default no-op behavior.

    All OpenTracing implementations MUST formally subclass Tracer (in order to
    inherit OPENTRACING_PYTHON_API_SEMVER if nothing else).
    """


    singleton_noop_span = Span()

    def start_trace(self, operation_name=None, tags=None):
        """Starts a new trace and creates a new root span.

        This method should be used by services that are instrumented for
        tracing but did not receive trace ID from upstream request.

        :param operation_name: the service's own name for the end-point
            that received the request represented by this trace and span.
            The domain of names must be limited, e.g. do not use UUIDs or
            entity IDs or timestamps as part of the name.
        :param tags: optional dictionary of Span Tags. The caller is
            expected to give up ownership of that dictionary, because the
            Tracer may use it as is to avoid extra data copying.

        :return: a new root Span
        """
        return Tracer.singleton_noop_span

    def join_trace(self, operation_name, parent_span, tags=None):
        """Joins a trace started elsewhere and creates a new span as a
        child of the given parent trace context.

        This method should be used by services that receive tracing info
        from upstream.

        :param operation_name: the service's own name for the end-point
            that received the request represented by this trace and span.
            The domain of names must be limited, e.g. do not use UUIDs or
            entity IDs or timestamps as part of the name.
        :param parent_span: a Span instance started elsewhere and whose trace
            we're joining.
        :param tags: optional dictionary of Span Tags. The caller is
            expected to give up ownership of that dictionary, because the
            Tracer may use it as is to avoid extra data copying.

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

    # The OpenTracing Python API's SemVer (http://semver.org/). Note that each
    # OpenTracing platform API has its own semver (which has more to do with
    # refactors or other compatibility changes and less to do with the
    # platform-independent OpenTracing semantic specification).
    #
    # Note that -- with vendored code buried within vendored code -- it is
    # possible (though not particularly desirable) for a single Python process
    # to have more than one OpenTracing implementation contained within, and
    # perhaps at different API SemVers. As such, OpenTracing users who want to
    # know the API SemVer should always do so via a Tracer instance.
    #
    #     if tracer_var.OPENTRACING_PYTHON_API_SEMVER == ...
    #
    OPENTRACING_PYTHON_API_SEMVER = '0.9.0'
