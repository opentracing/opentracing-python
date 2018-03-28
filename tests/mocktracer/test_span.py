from opentracing.mocktracer import MockTracer


def test_span_log_kv():
    tracer = MockTracer()

    span = tracer.start_span('x')
    span.log_kv({
        'foo': 'bar',
        'baz': 42,
        })
    span.finish()

    finished_spans = tracer.finished_spans()
    assert len(finished_spans) == 1
    assert len(finished_spans[0].logs) == 1
    assert len(finished_spans[0].logs[0].key_values) == 2
    assert finished_spans[0].logs[0].key_values['foo'] == 'bar'
    assert finished_spans[0].logs[0].key_values['baz'] == 42
