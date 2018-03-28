# Copyright The OpenTracing Authors

from __future__ import absolute_import
from opentracing import child_of
from opentracing import Tracer


def test_tracer():
    tracer = Tracer()
    span = tracer.start_span(operation_name='root')
    child = tracer.start_span(operation_name='child',
                              references=child_of(span))
    assert span == child
