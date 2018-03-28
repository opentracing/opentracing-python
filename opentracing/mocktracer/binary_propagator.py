# Copyright (c) 2018 The OpenTracing Authors.
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

import pickle

from .context import SpanContext
from .propagator import Propagator

from opentracing import InvalidCarrierException, SpanContextCorruptedException


class BinaryPropagator(Propagator):
    """A MockTracer Propagator for Format.BINARY."""

    def inject(self, span_context, carrier):
        if type(carrier) is not bytearray:
            raise InvalidCarrierException()
        state = TracerState()
        state.trace_id = span_context.trace_id
        state.span_id = span_context.span_id
        if span_context.baggage is not None:
            for key in span_context.baggage:
                state.baggage_items[key] = span_context.baggage[key]

        data = pickle.dumps(state)
        carrier.extend(data)

    def extract(self, carrier):
        if type(carrier) is not bytearray:
            raise InvalidCarrierException()

        try:
            state = pickle.loads(carrier)
        except (EOFError, pickle.PickleError):
            raise SpanContextCorruptedException()

        baggage = {}
        for k in state.baggage_items:
            baggage[k] = state.baggage_items[k]

        return SpanContext(
            span_id=state.span_id,
            trace_id=state.trace_id,
            baggage=baggage)


class TracerState(object):
    def __init__(self):
        self.trace_id = -1
        self.span_id = -1
        self.baggage_items = {}
