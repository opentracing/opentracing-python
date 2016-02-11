# Copyright (c) 2016 The OpenTracing Authors.
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

from .span import Span


class SpanPropagator(object):
    """SpanPropagator encodes and decodes Spans between processes.

    SpanPropagator is responsible (a) for encoding Span instances in a manner
    suitable for propagation, and (b) for taking that encoded data and using it
    to generate Span instances that are placed appropriately in the overarching
    Trace. Typically the propagation will take place across an RPC boundary,
    but message queues and other IPC mechanisms are also reasonable places to
    use a SpanPropagator.

    The encoded form of a propagated span is divided into two components:

      1) The Tracer-internal state ("Tracer State") for the Span (for example,
         in Dapper this would include a trace_id, a span_id, and a bitmask
         representing the sampling status for the given trace)
      2) Any trace attributes (per Span.set_trace_attribute)

    The encoded data is separated in this way for a variety of reasons; the
    most important is to give OpenTracing users a portable way to opt out of
    Trace Attribute propagation entirely if they deem it a stability risk.

    The propagate_span_as*() and join_trace_from_*() methods come in two
    flavors: binary and text. The text format is better-suited to
    pretty-printing and debugging, and the binary format is better-suited to
    compact, high-performance encoding, decoding, and transmission.
    """

    singleton_noop_span = Span()

    def propagate_span_as_binary(self, span):
        """Represents the Span for propagation as opaque binary data.

        :param span: the Span instance to propagate

        :rtype: ((bytearray, bytearray) or None)
        :return: A pair of bytearrays. The first element must represent the
            SpanPropagator's encoding of the Tracer State for `span`. The
            second element must represent the SpanPropagator's encoding of any
            trace attributes, per `Span.set_trace_attribute`.
        """
        return bytearray(), None

    def propagate_span_as_text(self, span):
        """Represents the Span for propagation as a pair of text dicts.

        :param span: the Span instance to propagate

        :rtype: ((dict, dict) or None)
        :return: A pair of text->text dicts. The first element must represent
            the SpanPropagator's encoding of the Tracer State for `span`. The
            second element must represent the SpanPropagator's encoding of any
            trace attributes, per `Span.set_trace_attribute`.
        """
        return {}, None

    def join_trace_from_binary(self, operation_name, tracer_state, trace_attributes):
        """Starts and returns a new Span with the given `operation_name`.

        The returned Span instance is joined to whatever remote Span was
        binary-encoded as (`tracer_state`, `trace_attributes`).

        :param operation_name: the operation name for the returned Span, or
            None if the caller prefers to call `Span.set_operation_name()`
            directly.
        :param tracer_state: tracer state encoded as a bytearray
        :param trace_attributes: Trace Attributes encoded as a bytearray

        :return: a started Span instance
        """
        return SpanPropagator.singleton_noop_span

    def join_trace_from_text(self, operation_name, tracer_state, trace_attributes):
        """Starts and returns a new Span with the given `operation_name`.

        The returned Span instance is joined to whatever remote Span was
        text-encoded as (`tracer_state`, `trace_attributes`).

        It's permissible to pass the same dict to both `tracer_state` and
        `trace_attributes` (e.g., an HTTP request headers map): the
        implementation should only decode the subset of keys it's interested
        in.

        :param operation_name: the operation name for the returned Span, or
            None if the caller prefers to call `Span.set_operation_name()`
            directly.
        :param tracer_state: tracer state encoded as a string->string dict
        :param trace_attributes: Trace Attributes encoded as a string->string dict

        :return: a started Span instance
        """
        return SpanPropagator.singleton_noop_span
