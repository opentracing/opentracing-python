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


class Tracer(object):
    """Tracer is the entry point API between instrumentation code and the
    tracing implementation.

    This implementation both defines the public Tracer API, and provides
    a default no-op behavior.
    """

    def __init__(self):
        self._noop_span = Span(self)

    def start_span(self,
                   operation_name=None,
                   parent=None,
                   tags=None,
                   start_time=None):
        """Starts and returns a new Span representing a unit of work.

        :param operation_name: name of the operation represented by the new
            span from the perspective of the current service.
        :param parent: an optional parent Span. If specified, the returned Span
            will be a child of `parent` in `parent`'s trace. If unspecified,
            the returned Span will be the root of its own trace.
        :param tags: optional dictionary of Span Tags. The caller gives up
            ownership of that dictionary, because the Tracer may use it as-is
            to avoid extra data copying.
        :param start_time: an explicit Span start time as a unix timestamp per
            time.time()

        :return: Returns an already-started Span instance.
        """
        return self._noop_span

    def inject(self, span, format, carrier):
        """Injects `span` into `carrier`.

        The type of `carrier` is determined by `format`. See the
        opentracing.propagation.Format class/namespace for standard (and
        required) formats.

        Implementations may raise opentracing.UnsupportedFormatException if
        `format` is unknown or disallowed.

        :param span: the Span instance to inject
        :param format: a python object instance that represents a given
            carrier format. `format` may be of any type, and `format` equality
            is defined by python `==` equality.
        :param carrier: the format-specific carrier object to inject into
        """
        pass

    def join(self, operation_name, format, carrier):
        """Returns a Span instance with operation name `operation_name`
        that's joined to the trace state embedded within `carrier`, or None if
        no such trace state could be found.

        The type of `carrier` is determined by `format`. See the
        opentracing.propagation.Format class/namespace for standard (and
        required) formats.

        Implementations may raise opentracing.UnsupportedFormatException if
        `format` is unknown or disallowed.

        Implementations may raise opentracing.InvalidCarrierException,
        opentracing.TraceCorruptedException, or implementation-specific errors
        if there are problems with `carrier`.

        Upon success, the returned Span instance is already started.

        :param operation_name: the operation name for the returned Span (which
            can be set later via Span.set_operation_name())
        :param format: a python object instance that represents a given
            carrier format. `format` may be of any type, and `format` equality
            is defined by python `==` equality.
        :param carrier: the format-specific carrier object to join with

        :return: a Span instance joined to the trace state in `carrier` or None
            if no such trace state could be found.
        """
        return self._noop_span

    def flush(self):
        """Flushes any trace data that may be buffered in memory, presumably
        out of the process.

        :return: Returns a :py:class:futures.Future
        """
        fut = Future()
        fut.set_result(True)
        return fut
