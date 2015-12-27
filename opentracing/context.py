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
    """Represents the identity of a given Span and metadata of the trace.

    The span identity is embedded in this context in implementation-specific
    format. The contents are serialized on the wire during inter-process calls.

    Metadata can be added to the context and will be available to all
    future spans in the call tree rooted at the current span, but will not
    propagate up the call tree.

    The more metadata is added to the context, the heavier it makes the
    requests on the wire, so it must be used with caution.
    """

    def new_child(self):
        """Creates a child context of the current context.

        Since this is a no-op implementation, it returns itself as a child.
        Actual implementation must create a new context that is a logical
        child of the current context.

        :rtype : (TraceContext, dict)
        :return: a pair of (child_context, child_tags), where child_tags is
            an optional dictionary of tags to be added to the child span.
        """
        return self, dict()

    def set_metadata(self, key, value):
        """Adds metadata to the trace.

        Enables powerful distributed context propagation functionality where
        arbitrary set of metadata can be carried along the full path of
        request execution throughout the system.

        Note 1: metadata is only propagated to the future children of the
        current trace context.

        Note 2: metadata is sent in-band with every subsequent local and
        remote calls, so this feature must be used with care.

        Note 3: keys are case-insensitive, to allow propagation of metadata
        via HTTP headers. Keys must match rexep `(?i:[a-z0-9][-a-z0-9]*)`

        :param key: key of the metadata
        :type key: str

        :param value: value of the metadata
        :type vaue: str

        :rtype : TraceContext
        :return: itself, for chaining the calls.
        """
        return self

    def get_metadata(self, key):
        """Retrieves metadata value for a given key.

        Key is always converted to upper case.

        :param key: key of the metadata
        :type key: str

        :rtype : str
        :return: value of the metadata with given key, or None.
        """
        return None

    # def get_all_metadata(self):
    #     """Returns metadata as a cloned dictionary."""
    #     # TODO revisit if this needs to be in public API
    #     return dict()


class TraceContextMarshaler(object):
    """Allows marshaling a trace context binary or string formats.

    The marshaler is expected to serialize trace contexts into a pair of
    values representing separately the trace context / span identity,
    and the metadata tags. This is done specifically for binary protocols
    that may represent tracing identity in a dedicated fixed-length slot
    in the binary message format, so that it can be inspected efficiently
    by the middleware / routing layers without parsing the whole message.
    """

    def marshal_trace_context_binary(self, trace_context):
        """Converts trace context to a pair of bytearray's representing
        separately span identity and metadata.

        :param trace_context: trace context to marshal
        :type trace_context: TraceContext

        :return: a pair of bytearray's, first representing the span identity,
            the second representing metadata key/value pairs.
        """
        return bytearray(), bytearray()

    def marshal_trace_context_str_dict(self, trace_context):
        """Converts trace context to a pair of dict's representing
        separately span identity and metadata.

        :param trace_context: trace context to marshal
        :type trace_context: TraceContext

        :return: a pair of str dicts, first representing the span identity,
            the second representing metadata key/value pairs.
        """
        return dict(), dict()


class TraceContextUnmarshaler(object):
    """Allows unmarshaling a trace context from binary or string formats."""

    def unmarshal_trace_context_binary(self, trace_context_id, metadata):
        """Converts marshaled binary data into a TraceContext.

        Singe this is a reference no-op implementation, it always returns
        two same singleton context.

        Args:
            trace_context_id (bytearray): span identity
            trace_tags (bytearray): metadata tags

        Returns:
            a reconstructed TraceContext.
        """
        return TraceContextSource.singleton_noop_trace_context

    def unmarshal_trace_context_str_dict(self, trace_context_id, metadata):
        """Converts marshaled string data into a TraceContext.

        Singe this is a reference no-op implementation, it always returns
        two same singleton context.

        Args:
            trace_context_id (dict): span identity as string->string map
            trace_tags (dict): metadata tags as string->string map

        Returns:
            a reconstructed TraceContext.
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

        Returns:
            a new trace context without parent.
        """
        return TraceContextSource.singleton_noop_trace_context
