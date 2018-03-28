from opentracing.mocktracer import MockTracer


def test_tracer_finished_spans():
    tracer = MockTracer()

    span_x = tracer.start_span('x')
    span_x.finish()

    span_y = tracer.start_span('y')
    span_y.finish()

    finished_spans = tracer.finished_spans()
    assert len(finished_spans) == 2
    assert finished_spans[0] == span_x
    assert finished_spans[1] == span_y

    # A copy per invocation.
    assert tracer.finished_spans() is not finished_spans


def test_tracer_reset():
    tracer = MockTracer()
    tracer.start_span('x').finish()
    tracer.reset()
    assert len(tracer.finished_spans()) == 0
