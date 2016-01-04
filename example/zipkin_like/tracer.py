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
import time

from tchannel.net import local_ip

import opentracing
from . import glossary
from .glossary import TRACE_ATTRIBUTES_HEADER_PREFIX
from .marshaling import TraceContextMarshaler, TraceContextUnmarshaler
from .span import Span
from .version import __version__
from .thrift import ipv4_to_int


class Tracer(opentracing.Tracer):
    def __init__(self, service_name, reporter, trace_context_source):
        self.service_name = service_name
        self.reporter = reporter
        self.trace_context_source = trace_context_source
        self.ip_address = ipv4_to_int(local_ip())
        self.encoder = TraceContextMarshaler(
            trace_id_header=glossary.TRACE_ID_HEADER,
            trace_attributes_header_prefix=TRACE_ATTRIBUTES_HEADER_PREFIX)
        self.decoder = TraceContextUnmarshaler(
            trace_id_header=glossary.TRACE_ID_HEADER,
            trace_attributes_header_prefix=TRACE_ATTRIBUTES_HEADER_PREFIX)

    def start_trace(self, operation_name, debug=False):
        """Implements start_trace of opentracing.Tracer."""
        trace_context = self.trace_context_source.new_root_trace_context(debug)
        return self.create_span(operation_name=operation_name,
                                trace_context=trace_context,
                                is_client=False)

    def join_trace(self, operation_name, parent_trace_context):
        """Implements join_trace of opentracing.Tracer"""
        # NOTE: Zipkin-specific behavior - server joins the same span that
        # was started by the client.
        return self.create_span(operation_name=operation_name,
                                trace_context=parent_trace_context,
                                is_client=False)

    def close(self):
        """Performs a clean shutdown of the tracer, flushing any traces that
        may be buffered in memory.

        :return: Returns a concurrent.futures.Future that indicates if the
            flush has been completed.
        """
        self.trace_context_source.close()
        return self.reporter.close()

    def create_span(self, operation_name, trace_context, is_client, tags=None):
        """
        Internal method
        """
        span = Span(trace_context=trace_context,
                    tracer=self,
                    operation_name=operation_name,
                    is_client=is_client)
        if tags:
            for k, v in tags.iteritems():
                span.add_tag(k, v)
        span.ts = self.timestamp()
        span.add_tag(key='tracing.client', value='Python-%s' % __version__)
        return span

    def report_span(self, span):
        self.reporter.report_span(span)

    @staticmethod
    def timestamp():
        """Returns current time in microseconds."""
        return time.time() * 1000000

    def marshal_trace_context_binary(self, trace_context):
        return self.encoder.marshal_trace_context_binary(
            trace_context=trace_context
        )

    def marshal_trace_context_str_dict(self, trace_context):
        return self.encoder.marshal_trace_context_str_dict(
            trace_context=trace_context
        )

    def unmarshal_trace_context_binary(self, trace_context_id,
                                       trace_attributes):
        return self.decoder.unmarshal_trace_context_binary(
            trace_context_id=trace_context_id,
            trace_attributes=trace_attributes
        )

    def unmarshal_trace_context_str_dict(self, trace_context_id,
                                         trace_attributes):
        return self.decoder.unmarshal_trace_context_str_dict(
            trace_context_id=trace_context_id,
            trace_attributes=trace_attributes
        )
