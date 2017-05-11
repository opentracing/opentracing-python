from __future__ import absolute_import
from opentracing import Tracer
from opentracing.ext import globaltracer
import mock

def reset_globaltracer():
    globaltracer._GlobalTracer.reset()

def test_get():
    reset_globaltracer()
    tracer = globaltracer.get()
    assert tracer is not None

def test_register_none():
    reset_globaltracer()
    value_error = False
    try:
        globaltracer.register(None)
    except ValueError:
        value_error = True

    assert value_error == True

def test_register_global():
    reset_globaltracer()
    globaltracer.register(globaltracer.get())

def test_register_same():
    reset_globaltracer()
    tracer = mock.Mock(spec=Tracer)
    globaltracer.register(tracer)

def test_register_already():
    reset_globaltracer()
    value_error = False
    globaltracer.register(mock.Mock(spec=Tracer))
    try:
        globaltracer.register(mock.Mock(spec=Tracer))
    except ValueError:
        value_error = True

    assert value_error == True

def test_start_span():
    reset_globaltracer()
    tracer = mock.Mock(spec=Tracer)
    globaltracer.register(tracer)

    span = globaltracer.get().start_span(1, 2, 3, 4, 5)
    assert span is not None
    assert tracer.start_span.call_count == 1
    assert tracer.start_span.call_args == ((1, 2, 3, 4, 5),)

def test_extract():
    reset_globaltracer()
    tracer = mock.Mock(spec=Tracer)
    globaltracer.register(tracer)

    globaltracer.get().extract(1, 2)
    assert tracer.extract.call_count == 1
    assert tracer.extract.call_args == ((1, 2),)

def test_inject():
    reset_globaltracer()
    tracer = mock.Mock(spec=Tracer)
    globaltracer.register(tracer)

    globaltracer.get().inject(1, 2, 3)
    assert tracer.inject.call_count == 1
    assert tracer.inject.call_args == ((1, 2, 3),)

