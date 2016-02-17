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


class Injector(object):
    """An Injector injects Span instances into a format-specific "carrier"
    object.

    Typically the carrier will then propagate across a process boundary, often
    via an RPC (though message queues and other IPC mechanisms are also
    reasonable places to use an Injector).

    See Extractor and Tracer.injector().
    """

    def inject_span(self, span, carrier):
        """inject_span takes `span` and injects it into `carrier`.

        The actual type of `carrier` depends on the `format` value passed to
        `Tracer.injector()`.

        Implementations may raise opentracing.InvalidCarrierException or any
        other implementation-specific exception if injection fails.

        :param span: the Span instance to inject
        :param carrier: the format-specific carrier object to inject into
        """
        raise NotImplementedError()


class Extractor(object):
    """An Extractor extracts Span instances from a format-specific "carrier"
    object.

    Typically the carrier has just arrived across a process boundary, often via
    an RPC (though message queues and other IPC mechanisms are also reasonable
    places to use an Extractor).

    See Injector and Tracer.extractor().
    """

    def join_trace(self, operation_name, carrier):
        """join_trace returns a Span instance with operation name `operation_name`
        that's joined to the trace state embedded within `carrier`, or None if
        no such trace state could be found.

        Implementations may raise opentracing.InvalidCarrierException,
        opentracing.TraceCorruptedException, or implementation-specific errors
        if there are more fundamental problems with `carrier`.

        Upon success, the returned Span instance is already started.

        :param operation_name: the operation name for the returned Span (which
            can be set later via Span.set_operation_name())
        :param carrier: the format-specific carrier object to extract from

        :return: a Span instance joined to the trace state in `carrier` or None
            if no such trace state could be found.
        """
        raise NotImplementedError()


class InvalidCarrierException(Exception):
    """InvalidCarrierException should be used when the provided carrier
    instance does not match what the `format` argument requires.

    See Injector and Extractor.
    """
    pass


class TraceCorruptedException(Exception):
    """TraceCorruptedException should be used when the underlynig trace state
    is seemingly present but not well-formed.

    See Extractor.join_trace.
    """
    pass


class Format:
    """A namespace for builtin Injector/Extractor formats.

    These static constants are intended for use in the Tracer.injector() and
    Tracer.extractor() methods. E.g.,

        tracer.injector(Format.SPLIT_BINARY).inject_span(...)

    """

    # The SPLIT_BINARY format pairs with an Injector or Extractor that expects
    # a SplitBinaryCarrier carrier object.
    SPLIT_BINARY = 'split_binary'

    # The SPLIT_TEXT format pairs with an Injector or Extractor that expects a
    # SplitTextCarrier carrier object.
    SPLIT_TEXT = 'split_text'


class SplitBinaryCarrier(object):
    """The SplitBinaryCarrier is a carrier to be used with Format.SPLIT_BINARY
    Injectors/Extractors.

    The SplitBinaryCarrier has two properties, and each is represented as a
    bytearray:
     - tracer_state: Tracer-specific context that must cross process
       boundaries. For example, in Dapper this would include a trace_id, a
       span_id, and a bitmask representing the sampling status for the given
       trace.
     - trace_attributes: any Trace Attributes for the encoded Span (per
       Span.SetTraceAttribute).
    """

    def __init__(self, tracer_state=None, trace_attributes=None):
        self.tracer_state = (
            bytearray() if tracer_state is None else tracer_state)
        self.trace_attributes = (
            bytearray() if trace_attributes is None else trace_attributes)


class SplitTextCarrier(object):
    """The SplitTextCarrier is a carrier to be used with Format.SPLIT_BINARY
    Injectors/Extractors.

    The SplitTextCarrier has two properties, and each is represented as a
    string->string dict:
     - tracer_state: Tracer-specific context that must cross process
       boundaries. For example, in Dapper this would include a trace_id, a
       span_id, and a bitmask representing the sampling status for the given
       trace.
     - trace_attributes: any Trace Attributes for the encoded Span (per
       Span.SetTraceAttribute).
    """

    def __init__(self, tracer_state=None, trace_attributes=None):
        self.tracer_state = (
            {} if tracer_state is None else tracer_state)
        self.trace_attributes = (
            {} if trace_attributes is None else trace_attributes)


class _NoopPropagator:
    def __init__(self, tracer):
        self._tracer = tracer

    def inject_span(self, span, carrier):
        pass

    def join_trace(self, operation_name, carrier):
        return self._tracer._noop_span
