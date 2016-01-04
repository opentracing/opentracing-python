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
import opentracing
from .context import TraceContext


class TraceContextMarshaler(opentracing.TraceContextMarshaler):
    """
    Implements opentracing.TraceContextMarshaler.
    """
    def __init__(self, trace_id_header, trace_attributes_header_prefix):
        self.prefix = trace_attributes_header_prefix.lower()
        self.prefix_length = len(trace_attributes_header_prefix)
        self.trace_id_header = trace_id_header.lower().replace('_', '-')

    def marshal_trace_context_binary(self, trace_context):
        raise NotImplementedError('marshal_trace_context_binary')

    def marshal_trace_context_str_dict(self, trace_context):
        """Converts trace context to a pair of dict's representing
        separately span identity and Trace Attributes.

        :param trace_context: trace context to marshal
        :type trace_context: TraceContext

        :return: a pair of str dicts, first representing the span identity,
            the second representing Trace Attributes.
        """
        ctx_id = TraceContextMarshaler.id_to_string(trace_context)
        span_id_out = {self.trace_id_header: ctx_id}
        trace_attributes = trace_context.trace_attributes_as_dict()
        trace_attributes_out = None
        if trace_attributes is not None:
            trace_attributes_out = {}
            for key, value in trace_attributes.iteritems():
                trace_attributes_out['%s%s' % (self.prefix, key)] = value
        return span_id_out, trace_attributes_out

    @staticmethod
    def id_to_string(trace_context):
        """
        Serialize span ID from the trace context to a string
        ``{trace_id}:{span_id}:{parent_id}:{flags}.``
        Number are encoded as variable-length lower-case hex strings.
        If parent_id is None, it is written as 0.
        """
        parent_id = trace_context.parent_id \
            if trace_context.parent_id is not None \
            else 0L
        return "{:x}:{:x}:{:x}:{:x}".format(trace_context.trace_id,
                                            trace_context.span_id,
                                            parent_id,
                                            trace_context.flags)


class TraceContextUnmarshaler(opentracing.TraceContextUnmarshaler):

    def __init__(self, trace_id_header, trace_attributes_header_prefix):
        self.prefix = trace_attributes_header_prefix.lower()
        self.prefix_length = len(trace_attributes_header_prefix)
        self.trace_id_header = trace_id_header.lower().replace('_', '-')

    def unmarshal_trace_context_binary(self, trace_context_id,
                                       trace_attributes):
        raise NotImplementedError('unmarshal_trace_context_binary')

    def unmarshal_trace_context_str_dict(self, trace_context_id,
                                         trace_attributes):
        ctx_id = trace_context_id.get(self.trace_id_header, None)
        if ctx_id is None:
            return None
        trace_context = TraceContextUnmarshaler.\
            trace_context_from_string(value=ctx_id)
        if trace_context is None:
            return None
        trace_attributes_out = None
        if trace_attributes:
            for key, value in trace_attributes.iteritems():
                uc_key = key.lower()
                if uc_key.startswith(self.prefix):
                    attr_key = key[self.prefix_length:]
                    if trace_attributes_out is None:
                        trace_attributes_out = {attr_key.lower(): value}
                    else:
                        trace_attributes_out[attr_key.lower()] = value
        if trace_attributes_out is not None:
            trace_context.append_trace_attributes(trace_attributes_out)
        return trace_context

    @staticmethod
    def trace_context_from_string(value):
        """
        Decodes span ID from a string into a TraceContext.
        Returns None if the string value is malformed.
        """
        if type(value) is list and len(value) > 0:
            # sometimes headers are presented as arrays of values
            value = value[0]
        if type(value) is not str:
            return None
        parts = value.split(':')
        if len(parts) != 4:
            return None
        try:
            trace_id = long(parts[0], 16)
            span_id = long(parts[1], 16)
            parent_id = long(parts[2], 16)
            flags = int(parts[3], 16)
            if trace_id < 1 or span_id < 1 or parent_id < 0 or flags < 0:
                return None
            if parent_id == 0:
                parent_id = None
            return TraceContext(trace_id=trace_id, span_id=span_id,
                                parent_id=parent_id, flags=flags)
        except ValueError:
            return None
