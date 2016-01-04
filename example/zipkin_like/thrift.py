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

import socket
import struct

from .zipkin_thrift import zipkin_collector


def ipv4_to_int(ipv4):
    if ipv4 == 'localhost':
        ipv4 = '127.0.0.1'
    elif ipv4 == '::1':
        ipv4 = '127.0.0.1'
    try:
        return struct.unpack('!i', socket.inet_aton(ipv4))[0]
    except:
        return 0


def port_to_int(port):
    if type(port) is str:
        if port.isdigit():
            port = int(port)
    if type(port) is int:
        # zipkinCore.thrift defines port as i16, which is signed,
        # therefore we convert ephemeral ports as negative ints
        if port >= 32768:
            port -= (1 << 16)
        return port
    return None


def make_endpoint(ipv4, port, service_name):
    if type(ipv4) is str:
        ipv4 = ipv4_to_int(ipv4)
    port = port_to_int(port)
    if port is None:
        port = 0
    return zipkin_collector.Endpoint(ipv4, port, service_name.lower())


def make_string_tag(key, value):
    return zipkin_collector.BinaryAnnotation(
        key, value, zipkin_collector.AnnotationType.STRING)


def make_peer_address_tag(key, host):
    """
    Used for Zipkin binary annotations like CA/SA (client/server address).
    They are modeled as Boolean type with '0x01' as the value.
    """
    return zipkin_collector.BinaryAnnotation(
        key, '0x01', zipkin_collector.AnnotationType.BOOL, host)


def make_event(timestamp=None, name=None):
    return zipkin_collector.Annotation(
        timestamp=long(timestamp), value=name, host=None)


def make_zipkin_spans(spans):
    zipkin_spans = []
    for span in spans:
        ctx = span.trace_context
        endpoint = make_endpoint(ipv4=span.tracer.ip_address,
                                 port=0,  # span.port,
                                 service_name=span.tracer.service_name)
        # TODO extend Zipkin Thrift and pass endpoint once only
        for event in span.logs:
            event.host = endpoint
        zipkin_span = zipkin_collector.Span(
            trace_id=ctx.trace_id,
            name=span.operation_name,
            id=ctx.span_id,
            parent_id=ctx.parent_id,
            annotations=span.logs,
            binary_annotations=span.tags,
            debug=span.is_debug(),
            timestamp=long(span.ts),
            duration=long(span.duration)
        )
        zipkin_spans.append(zipkin_span)
    return zipkin_spans


def make_submit_batch_request(spans):
    zipkin_spans = make_zipkin_spans(spans)
    return zipkin_collector.ZipkinCollector.submitZipkinBatch(zipkin_spans)
