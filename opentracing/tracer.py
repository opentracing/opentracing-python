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
from collections import namedtuple
from .span import Span
from .span import SpanContext
from .propagation import Format, UnsupportedFormatException


class Tracer(object):
    """Tracer is the entry point API between instrumentation code and the
    tracing implementation.

    This implementation both defines the public Tracer API, and provides
    a default no-op behavior.
    """

    _supported_formats = [Format.TEXT_MAP, Format.BINARY, Format.HTTP_HEADERS]

    def __init__(self):
        self._noop_span_context = SpanContext()
        self._noop_span = Span(tracer=self, context=self._noop_span_context)

    def start_span(self,
                   operation_name=None,
                   child_of=None,
                   references=None,
                   tags=None,
                   start_time=None):
        """Starts and returns a new Span representing a unit of work.


        Starting a root Span (a Span with no causal references):

            tracer.start_span('...')


        Starting a child Span (see also start_child_span()):

            tracer.start_span(
                '...',
                child_of=parent_span)


        Starting a child Span in a more verbose way:

            tracer.start_span(
                '...',
                references=[opentracing.child_of(parent_span)])


        :param operation_name: name of the operation represented by the new
            span from the perspective of the current service.
        :param child_of: (optional) a Span or SpanContext instance representing
            the parent in a REFERENCE_CHILD_OF Reference. If specified, the
            `references` parameter must be omitted.
        :param references: (optional) a list of Reference objects that identify
            one or more parent SpanContexts. (See the Reference documentation
            for detail)
        :param tags: an optional dictionary of Span Tags. The caller gives up
            ownership of that dictionary, because the Tracer may use it as-is
            to avoid extra data copying.
        :param start_time: an explicit Span start time as a unix timestamp per
            time.time()

        :return: Returns an already-started Span instance.
        """
        return self._noop_span

    def inject(self, span_context, format, carrier):
        """Injects `span_context` into `carrier`.

        The type of `carrier` is determined by `format`. See the
        opentracing.propagation.Format class/namespace for the built-in
        OpenTracing formats.

        Implementations MUST raise opentracing.UnsupportedFormatException if
        `format` is unknown or disallowed.

        :param span_context: the SpanContext instance to inject
        :param format: a python object instance that represents a given
            carrier format. `format` may be of any type, and `format` equality
            is defined by python `==` equality.
        :param carrier: the format-specific carrier object to inject into
        """
        if format in Tracer._supported_formats:
            return
        raise UnsupportedFormatException(format)

    def extract(self, format, carrier):
        """Returns a SpanContext instance extracted from a `carrier` of the
        given `format`, or None if no such SpanContext could be found.

        The type of `carrier` is determined by `format`. See the
        opentracing.propagation.Format class/namespace for the built-in
        OpenTracing formats.

        Implementations MUST raise opentracing.UnsupportedFormatException if
        `format` is unknown or disallowed.

        Implementations may raise opentracing.InvalidCarrierException,
        opentracing.SpanContextCorruptedException, or implementation-specific
        errors if there are problems with `carrier`.

        :param format: a python object instance that represents a given
            carrier format. `format` may be of any type, and `format` equality
            is defined by python `==` equality.
        :param carrier: the format-specific carrier object to extract from

        :return: a SpanContext instance extracted from `carrier` or None if no
            such span context could be found.
        """
        if format in Tracer._supported_formats:
            return self._noop_span_context
        raise UnsupportedFormatException(format)


class ReferenceType(object):
    """A namespace for OpenTracing reference types.

    See http://opentracing.io/spec for more detail about references,
    reference types, and CHILD_OF and FOLLOWS_FROM in particular.
    """
    CHILD_OF = 'child_of'
    FOLLOWS_FROM = 'follows_from'


# We use namedtuple since references are meant to be immutable.
# We subclass it to expose a standard docstring.
class Reference(namedtuple('Reference', ['type', 'referenced_context'])):
    """A Reference pairs a reference type with a referenced SpanContext.

    References are used by Tracer.start_span() to describe the relationships
    between Spans.

    Tracer implementations must ignore references where referenced_context is
    None.  This behavior allows for simpler code when an inbound RPC request
    contains no tracing information and as a result tracer.extract() returns
    None:

        parent_ref = tracer.extract(opentracing.HTTP_HEADERS, request.headers)
        span = tracer.start_span(
            'operation', references=child_of(parent_ref)
        )

    See `child_of` and `follows_from` helpers for creating these references.
    """
    pass


def child_of(referenced_context=None):
    """child_of is a helper that creates CHILD_OF References.

    :param referenced_context: the (causal parent) SpanContext to reference.
        If None is passed, this reference must be ignored by the tracer.

    :rtype: Reference
    :return: A Reference suitable for Tracer.start_span(..., references=...)
    """
    return Reference(
        type=ReferenceType.CHILD_OF,
        referenced_context=referenced_context)


def follows_from(referenced_context=None):
    """follows_from is a helper that creates FOLLOWS_FROM References.

    :param referenced_context: the (causal parent) SpanContext to reference
        If None is passed, this reference must be ignored by the tracer.

    :rtype: Reference
    :return: A Reference suitable for Tracer.start_span(..., references=...)
    """
    return Reference(
        type=ReferenceType.FOLLOWS_FROM,
        referenced_context=referenced_context)


def start_child_span(parent_span, operation_name, tags=None, start_time=None):
    """A shorthand method that starts a child_of span for a given parent span.

    Equivalent to calling

        parent_span.tracer().start_span(
            operation_name,
            references=opentracing.child_of(parent_span.context),
            tags=tags,
            start_time=start_time)

    :param parent_span: the Span which will act as the parent in the returned
        Span's child_of reference.
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
        child_of=parent_span,
        tags=tags,
        start_time=start_time
    )
