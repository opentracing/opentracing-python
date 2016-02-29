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


class UnsupportedFormatException(Exception):
    """UnsupportedFormatException should be used when the provided format
    value is unknown or disallowed by the Tracer.

    See Tracer.inject() and Tracer.join().
    """
    pass


class InvalidCarrierException(Exception):
    """InvalidCarrierException should be used when the provided carrier
    instance does not match what the `format` argument requires.

    See Tracer.inject() and Tracer.join().
    """
    pass


class TraceCorruptedException(Exception):
    """TraceCorruptedException should be used when the underlynig trace state
    is seemingly present but not well-formed.

    See Tracer.inject() and Tracer.join().
    """
    pass


class Format:
    """A namespace for builtin carrier formats.

    These static constants are intended for use in the Tracer.inject() and
    Tracer.join() methods. E.g.,

        tracer.inject(span, Format.SPLIT_BINARY, split_binary_carrier)

    """

    # The SPLIT_BINARY format pairs with a SplitBinaryCarrier carrier object.
    SPLIT_BINARY = 'split_binary'

    # The SPLIT_TEXT format pairs with a SplitTextCarrier carrier object.
    SPLIT_TEXT = 'split_text'


class SplitBinaryCarrier(object):
    """The SplitBinaryCarrier is a carrier to be used with Format.SPLIT_BINARY.

    The SplitBinaryCarrier has two properties, and each is represented as a
    bytearray:
     - tracer_state: Tracer-specific context that must cross process
       boundaries. For example, in Dapper this would include a trace_id, a
       span_id, and a bitmask representing the sampling status for the given
       trace.
     - baggage: any Baggage items for the encoded Span (per
       Span.set_baggage_item()).
    """

    def __init__(self, tracer_state=None, baggage=None):
        self.tracer_state = (
            bytearray() if tracer_state is None else tracer_state)
        self.baggage = (
            bytearray() if baggage is None else baggage)


class SplitTextCarrier(object):
    """The SplitTextCarrier is a carrier to be used with Format.SPLIT_TEXT.

    The SplitTextCarrier has two properties, and each is represented as a
    string->string dict:
     - tracer_state: Tracer-specific context that must cross process
       boundaries. For example, in Dapper this would include a trace_id, a
       span_id, and a bitmask representing the sampling status for the given
       trace.
     - baggage: any Baggage items for the encoded Span (per
       Span.set_baggage_item()).
    """

    def __init__(self, tracer_state=None, baggage=None):
        self.tracer_state = (
            {} if tracer_state is None else tracer_state)
        self.baggage = (
            {} if baggage is None else baggage)
