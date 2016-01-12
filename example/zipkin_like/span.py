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
import threading

import opentracing
from opentracing.ext import tags as ext_tags
from .glossary import SERVER_SEND, SERVER_RECV, CLIENT_SEND, CLIENT_RECV
from .glossary import SERVER_ADDR, CLIENT_ADDR
from . import thrift

SAMPLED_FLAG = 0x01
DEBUG_FLAG = 0x02


class Span(opentracing.Span):
    """Implements opentracing.Span with Zipkin semantics. """

    def __init__(self, trace_context, tracer, operation_name, is_client=False):
        super(Span, self).__init__(trace_context)
        self.tracer = tracer
        self.operation_name = operation_name
        self.is_client = is_client
        self.peer = None
        self.ts = None
        self.duration = None
        self.update_lock = threading.Lock()
        # we store tags and logs as Zipkin native thrift BinaryAnnotation and
        # Annotation structures, to avoid creating intermediate objects
        self.tags = []
        self.logs = []

    def start_child(self, operation_name, tags=None):
        """Implements start_child() of opentracing.Span"""
        child_ctx, child_tags = self.tracer.trace_context_source. \
            new_child_trace_context(parent_trace_context=self.trace_context)

        span = self.tracer.create_span(operation_name=operation_name,
                                       trace_context=child_ctx,
                                       is_client=True,
                                       tags=child_tags)
        if tags:
            for k, v in tags.itemitems():
                span.set_tag(k, v)
        return span

    def finish(self):
        """Implements finish() of opentracing.Span"""
        if self.is_sampled():
            ts = self.tracer.timestamp()
            self.duration = ts - self.ts
            end_event = CLIENT_RECV if self.is_client else SERVER_SEND
            end_event = thrift.make_event(timestamp=ts, name=end_event)

            start_event = CLIENT_SEND if self.is_client else SERVER_RECV
            start_event = thrift.make_event(timestamp=self.ts,
                                            name=start_event)

            if self.peer:
                host = thrift.make_endpoint(
                    ipv4=self.peer.get('ipv4', 0),
                    port=self.peer.get('port', 0),
                    service_name=self.peer.get('service_name', ''))
                addr = SERVER_ADDR if self.is_client else CLIENT_ADDR
                peer = thrift.make_peer_address_tag(key=addr, host=host)
            else:
                peer = None

            with self.update_lock:
                self.logs.append(start_event)
                self.logs.append(end_event)
                if peer:
                    self.tags.append(peer)

            self.tracer.report_span(self)

    def set_tag(self, key, value):
        """Implements set_tag() method of opentracing.Span"""
        if self.is_sampled():
            special = SPECIAL_TAGS.get(key, None)
            if special is not None and callable(special):
                special(self, value)
            else:
                tag = thrift.make_string_tag(key, value)
                with self.update_lock:
                    self.tags.append(tag)
        return self

    def info(self, message, *payload):
        self.add_log(message, False, *payload)

    def error(self, message, *payload):
        self.add_log(message, True, *payload)

    def add_log(self, message, is_error, *payload):
        """Internal method"""
        if self.is_sampled():
            timestamp = self.tracer.timestamp()
            log = thrift.make_event(timestamp, message)
            # Since Zipkin format does not support logs with payloads,
            # we convert the payload to a tag with the same name as log.
            # Also, if the log was an error, we add yet another tag.
            if payload:
                tag = thrift.make_string_tag(message, str(payload))
            else:
                tag = None
            if is_error:
                err = thrift.make_string_tag(message, 'error')
            else:
                err = None
            with self.update_lock:
                self.logs.append(log)
                if tag:
                    self.tags.append(tag)
                if err:
                    self.tags.append(err)

    def is_sampled(self):
        return self.trace_context.flags & SAMPLED_FLAG == SAMPLED_FLAG

    def is_debug(self):
        return self.trace_context.flags & DEBUG_FLAG == DEBUG_FLAG

    def __str__(self):
        from .codecs import TraceContextEncoder

        id_str = TraceContextEncoder.id_to_string(self.trace_context)
        return "%s.%s %s" % (self.tracer.service_name,
                             self.operation_name,
                             id_str)


def _peer_service(span, value):
    with span.update_lock:
        if span.peer is None:
            span.peer = {'service_name': value}
        else:
            span.peer['service_name'] = value


def _peer_host_ipv4(span, value):
    with span.update_lock:
        if span.peer is None:
            span.peer = {'ipv4': value}
        else:
            span.peer['ipv4'] = value


def _peer_port(span, value):
    with span.update_lock:
        if span.peer is None:
            span.peer = {'port': value}
        else:
            span.peer['port'] = value


SPECIAL_TAGS = {
    ext_tags.PEER_SERVICE: _peer_service,
    ext_tags.PEER_HOST_IPV4: _peer_host_ipv4,
    ext_tags.PEER_PORT: _peer_port,
}
