import mock
from opentracing import Span
from opentracing.ext.threadlocalspansource import ThreadLocalActiveSpanSource


def test_make_active():
    source = ThreadLocalActiveSpanSource()
    span = Span(None, None)
    active_span = source.make_active(span)
    assert active_span == source.active_span
    assert active_span.wrapped == span


def test_deactivate():
    source = ThreadLocalActiveSpanSource()
    span = Span(None, None)

    with mock.patch.object(span, 'finish') as finish:
        active_span = source.make_active(span)
        active_span.deactivate()
        assert finish.call_count == 1
        assert source.active_span is None


def test_context():
    source = ThreadLocalActiveSpanSource()
    span = Span(None, None)

    with mock.patch.object(span, 'finish') as finish:
        with mock.patch.object(span, 'log_kv') as log_kv:
            with source.make_active(span):
                pass

            assert finish.call_count == 1
            assert log_kv.call_count == 0
            assert source.active_span is None


def test_context_error():
    source = ThreadLocalActiveSpanSource()
    span = Span(None, None)

    with mock.patch.object(span, 'finish') as finish:
        with mock.patch.object(span, 'log_kv') as log_kv:

            try:
                with source.make_active(span):
                    raise ValueError()
            except ValueError:
                pass

            assert finish.call_count == 1
            assert log_kv.call_count == 1
            assert source.active_span is None


def test_capture():
    source = ThreadLocalActiveSpanSource()
    span = Span(None, None)

    with mock.patch.object(span, 'finish') as finish:
        active_span = source.make_active(span)
        continuation = active_span.capture()
        active_span.deactivate()

        assert finish.call_count == 0
        assert source.active_span is None

        active_span2 = continuation.activate()
        assert finish.call_count == 0
        assert source.active_span == active_span2

        active_span2.deactivate()
        assert finish.call_count == 1
        assert source.active_span is None


def test_wrong_order():
    source = ThreadLocalActiveSpanSource()
    span1 = source.make_active(Span(None, None))
    span2 = source.make_active(Span(None, None))
    assert span2 == source.active_span

    span1.deactivate()
    assert span2 == source.active_span
