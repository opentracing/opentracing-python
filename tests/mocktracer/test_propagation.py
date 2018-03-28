import pytest
from opentracing import Format, SpanContextCorruptedException, \
        UnsupportedFormatException
from opentracing.mocktracer import MockTracer


def test_propagation():
    tracer = MockTracer()
    sp = tracer.start_span(operation_name='test')
    sp.set_baggage_item('foo', 'bar')

    # Test invalid types
    with pytest.raises(UnsupportedFormatException):
        tracer.inject(sp.context, 'invalid', {})
    with pytest.raises(UnsupportedFormatException):
        tracer.extract('invalid', {})

    tests = [(Format.BINARY, bytearray()),
             (Format.TEXT_MAP, {})]
    for format, carrier in tests:
        tracer.inject(sp.context, format, carrier)
        extracted_ctx = tracer.extract(format, carrier)

        assert extracted_ctx.trace_id == sp.context.trace_id
        assert extracted_ctx.span_id == sp.context.span_id
        assert extracted_ctx.baggage == sp.context.baggage


def test_propagation_extract_corrupted_data():
    tracer = MockTracer()

    tests = [(Format.BINARY, bytearray()),
             (Format.TEXT_MAP, {})]
    for format, carrier in tests:
        with pytest.raises(SpanContextCorruptedException):
            tracer.extract(format, carrier)


def test_start_span():
    """ Test in process child span creation."""
    tracer = MockTracer()
    sp = tracer.start_span(operation_name='test')
    sp.set_baggage_item('foo', 'bar')

    child = tracer.start_span(
        operation_name='child', child_of=sp.context)
    assert child.context.trace_id == sp.context.trace_id
    assert child.context.baggage == sp.context.baggage
    assert child.parent_id == sp.context.span_id
