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

    singleton_noop_span = Span()

    def start_span(self, operation_name, parent=None, **kwargs):
        """Starts and returns a new Span representing a unit of work.

        :param operation_name: name of the operation represented by the new
            span from the perspective of the current service.
        :param parent: an optional parent Span. If specified, the returned Span
            will be a child of `parent` in `parent`'s trace. If unspecified,
            the returned Span will be the root of its own trace.
        :param tags: optional dictionary of Span Tags. The caller gives up
            ownership of that dictionary, because the Tracer may use it as is
            to avoid extra data copying.
        :param start_time: an explicit Span start timestamp as a unix timestamp
            per time.time()

        :return: Returns a new child Span in "started" state.
        """
        return Tracer.singleton_noop_span

    def injector(self, format):
        """Returns an Injector instance corresponding to `format`.

        See the opentracing.propagation module for standard (and required)
        formats.

        :param format: a python object instance that represents a given
            Injector format. `format` may be of any type, and `format` equality
            is defined by python `==` equality.

        :return: an Injector instance corresponding to `format`, or None if the
            Tracer implementation does not support `format`.
        """
        return None

    def extractor(self, format):
        """Returns an Extractor instance corresponding to `format`.

        See the opentracing.propagation module for standard (and required)
        formats.

        :param format: a python object instance that represents a given
            Extractor format. `format` may be of any type, and `format`
            equality is defined by python `==` equality.

        :return: an Extractor instance corresponding to `format`, or None if the
            Tracer implementation does not support `format`.
        """
        return None

    def close(self):
        """Performs a clean shutdown of the tracer, flushing any traces that
        may have been buffered in memory.

        :return: Returns a :py:class:futures.Future
        """
        fut = Future()
        fut.set_result(True)
        return fut
