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


class TraceContext(object):
    """Represents the identity of a given Span and Trace Attributes.

    The span identity is embedded in this context in implementation-specific
    format. The contents are serialized on the wire during inter-process calls.

    Trace Attributes can be added to the context and will be available to all
    future children of this span, but will not propagate up the call tree.

    The more attributes are added to the context, the heavier it makes the
    requests on the wire, so it must be used with caution.
    """

    def set_trace_attribute(self, key, value):
        """Stores Trace Attribute in the context as a key/value pair.

        Enables powerful distributed context propagation functionality where
        arbitrary application data can be carried along the full path of
        request execution throughout the system.

        Note 1: attributes are only propagated to the future children of the
        current trace context.

        Note 2: attributes are sent in-band with every subsequent local and
        remote calls, so this feature must be used with care.

        Note 3: keys are case-insensitive, to allow propagation  via HTTP
        headers. Keys must match rexep `(?i:[a-z0-9][-a-z0-9]*)`

        :param key: trace attribute key
        :type key: str

        :param value: trace attribute value
        :type value: str

        :rtype : TraceContext
        :return: itself, for chaining the calls.
        """
        return self

    def get_trace_attribute(self, key):
        """Retrieves value of the Trace Attribute with the given key.

        Key is case-insensitive.

        :param key: key of the Trace Attribute
        :type key: str

        :rtype : str
        :return: value of the Trace Attribute with given key, or None.
        """
        return None


class TraceContextEncoder(object):
    """Encodes a trace context in binary or text formats.

    The encoder is expected to serialize trace contexts into a pair of
    values representing separately the trace context / span identity,
    and the trace attributes. This is done specifically for binary protocols
    that may represent tracing identity in a dedicated fixed-length slot
    in the binary message format, so that it can be inspected efficiently
    by the middleware / routing layers without parsing the whole message.
    """

    def trace_context_to_binary(self, trace_context):
        """Converts trace context to a pair of bytearray's representing
        separately span identity and trace attributes.

        :param trace_context: trace context to encode
        :type trace_context: TraceContext

        :rtype (bytearray, bytearray or None)
        :return: a pair of bytearray's, first representing the span identity,
            the second representing Trace Attributes (can be None).
        """
        return bytearray(), None

    def trace_context_to_text(self, trace_context):
        """Converts trace context to a pair of dictionaries representing
        separately span identity and Trace Attributes.

        :param trace_context: trace context to encode
        :type trace_context: TraceContext

        :rtype (dict, dict or None)
        :return: a pair of string->string dictionaries, first representing the
            span identity, the second representing attributes (can be None).
        """
        return dict(), None


class TraceContextDecoder(object):
    """Decodes a trace context from binary or text formats."""

    def trace_context_from_binary(self, trace_context_id, trace_attributes):
        """Converts encoded binary data into a TraceContext.

        Singe this is a reference no-op implementation, it always returns
        two same singleton context.

        :param trace_context_id: span identity encoded as bytearray
        :param trace_attributes: attributes encoded as bytearray

        :return: a reconstructed TraceContext.
        """
        return TraceContextSource.singleton_noop_trace_context

    def trace_context_from_text(self, trace_context_id, trace_attributes):
        """Converts encoded string data into a TraceContext.

        Singe this is a reference no-op implementation, it always returns
        two same singleton context.

        :param trace_context_id: span identity encoded as string->string map
        :param trace_attributes: attributes encoded as string->string map

        :return: a reconstructed TraceContext.
        """
        return TraceContextSource.singleton_noop_trace_context


class TraceContextSource(object):
    """Knows how to create new TraceContext

    Since this is a reference no-op implementation, it always returns the
    same singleton context `singleton_noop_trace_context`.
    """

    singleton_noop_trace_context = TraceContext()

    def new_root_trace_context(self):
        """Creates a new TraceContext without parent and with unique identity.

        As the context has no parent, it implicitly starts a new trace.

        This is a no-op implementation that always returns the same context.

        :return: a new trace context without parent.
        """
        return TraceContextSource.singleton_noop_trace_context

    def new_child_trace_context(self, parent_trace_context):
        """Creates a child context from given parent context.

        Since this is a no-op implementation, it returns itself as a child.
        Actual implementation must create a new context that is a logical
        child of the current context.

        :param parent_trace_context: parent context

        :rtype : (TraceContext, dict or None)
        :return: a pair of (child_context, child_tags), where child_tags is
            an optional dictionary of tags to be added to the child span.
        """
        return TraceContextSource.singleton_noop_trace_context, None
