# Copyright (c) 2016 The OpenTracing Authors.
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

import mock
import time
import pytest

import opentracing
from opentracing import Format


class APICompatibilityCheckMixin(object):
    """
    A mixin class for validation that a given tracer implementation
    satisfies the requirements of the OpenTracing API.
    """

    def tracer(self):
        raise NotImplementedError('Subclass must implement tracer()')

    def check_baggage_values(self):
        """If true, the test will validate Baggage items by storing and
        retrieving them from the trace context. If false, it will only attempt
        to store and retrieve the Baggage items to check the API compliance,
        but not actually validate stored values. The latter mode is only
        useful for no-op tracer.
        """
        return True

    def check_scope_manager(self):
        """If true, the test suite will validate the `ScopeManager` propagation
        and storage to ensure the correct parenting and active `Scope` are
        properly defined by the implementation. If false, it will only use
        the API without any assert. The latter mode is only useful for no-op
        tracer.
        """
        return True

    def is_parent(self, parent, span):
        """Utility method that must be defined by Tracer implementers to define
        how the test suite can check when a `Span` is a parent of another one.
        """
        return False

    def test_start_span(self):
        # test for deprecated API
        tracer = self.tracer()
        span = tracer.start_span(operation_name='Fry')
        span.finish()
        with tracer.start_span(operation_name='Fry',
                               tags={'birthday': 'August 14 1974'}) as span:
            span.log_event('birthplace',
                           payload={'hospital': 'Brooklyn Pre-Med Hospital',
                                    'city': 'Old New York'})

    def test_start_active(self):
        # the first usage returns a `Scope` that wraps a root `Span`
        tracer = self.tracer()
        scope = tracer.start_active(operation_name='Fry')

        assert scope.span() is not None
        if self.check_scope_manager():
            assert self.is_parent(None, scope.span())

    def test_start_active_parent(self):
        # ensure the `ScopeManager` provides the right parenting
        tracer = self.tracer()
        with tracer.start_active(operation_name='Fry') as parent:
            with tracer.start_active(operation_name='Farnsworth') as child:
                if self.check_scope_manager():
                    assert self.is_parent(parent.span(), child.span())

    def test_start_active_ignore_active_scope(self):
        # ensure the `ScopeManager` ignores the active `Scope`
        # if the flag is set
        tracer = self.tracer()
        with tracer.start_active(operation_name='Fry') as parent:
            with tracer.start_active(operation_name='Farnsworth',
                                     ignore_active_scope=True) as child:
                if self.check_scope_manager():
                    assert not self.is_parent(parent.span(), child.span())

    def test_start_active_finish_on_close(self):
        # ensure a `Span` is finished when the `Scope` close
        tracer = self.tracer()
        scope = tracer.start_active(operation_name='Fry')
        with mock.patch.object(scope.span(), 'finish') as finish:
            scope.close()

        if self.check_scope_manager():
            assert finish.call_count == 1

    def test_start_active_not_finish_on_close(self):
        # a `Span` is not finished when the flag is set
        tracer = self.tracer()
        scope = tracer.start_active(operation_name='Fry',
                                    finish_on_close=False)
        with mock.patch.object(scope.span(), 'finish') as finish:
            scope.close()

        assert finish.call_count == 0

    def test_scope_as_context_manager(self):
        tracer = self.tracer()

        with tracer.start_active(operation_name='antiquing') as scope:
            assert scope.span() is not None

    def test_start_manual(self):
        tracer = self.tracer()
        span = tracer.start_manual(operation_name='Fry')
        span.finish()
        with tracer.start_manual(operation_name='Fry',
                                 tags={'birthday': 'August 14 1974'}) as span:
            span.log_event('birthplace',
                           payload={'hospital': 'Brooklyn Pre-Med Hospital',
                                    'city': 'Old New York'})

    def test_start_manual_propagation(self):
        # `start_manual` must inherit the current active `Scope` span
        tracer = self.tracer()
        with tracer.start_active(operation_name='Fry') as parent:
            with tracer.start_manual(operation_name='Farnsworth') as child:
                if self.check_scope_manager():
                    assert self.is_parent(parent.span(), child)

    def test_start_manual_propagation_ignore_active_scope(self):
        # `start_manual` doesn't inherit the current active `Scope` span
        # if the flag is set
        tracer = self.tracer()
        with tracer.start_active(operation_name='Fry') as parent:
            with tracer.start_manual(operation_name='Farnsworth',
                                     ignore_active_scope=True) as child:
                if self.check_scope_manager():
                    assert not self.is_parent(parent.span(), child)

    def test_start_manual_with_parent(self):
        tracer = self.tracer()
        parent_span = tracer.start_manual(operation_name='parent')
        assert parent_span is not None
        span = tracer.start_manual(
            operation_name='Leela',
            child_of=parent_span)
        span.finish()
        span = tracer.start_manual(
            operation_name='Leela',
            references=[opentracing.follows_from(parent_span.context)],
            tags={'birthplace': 'sewers'})
        span.finish()
        parent_span.finish()

    def test_start_child_span(self):
        tracer = self.tracer()
        parent_span = tracer.start_manual(operation_name='parent')
        assert parent_span is not None
        child_span = opentracing.start_child_span(
            parent_span, operation_name='Leela')
        child_span.finish()
        parent_span.finish()

    def test_set_operation_name(self):
        span = self.tracer().start_manual().set_operation_name('Farnsworth')
        span.finish()

    def test_span_as_context_manager(self):
        tracer = self.tracer()
        finish = {'called': False}

        def mock_finish(*_):
            finish['called'] = True

        with tracer.start_manual(operation_name='antiquing') as span:
            setattr(span, 'finish', mock_finish)
        assert finish['called'] is True

        # now try with exception
        finish['called'] = False
        try:
            with tracer.start_manual(operation_name='antiquing') as span:
                setattr(span, 'finish', mock_finish)
                raise ValueError()
        except ValueError:
            assert finish['called'] is True
        else:
            raise AssertionError('Expected ValueError')  # pragma: no cover

    def test_span_tag_value_types(self):
        with self.tracer().start_manual(operation_name='ManyTypes') as span:
            span. \
                set_tag('an_int', 9). \
                set_tag('a_bool', True). \
                set_tag('a_string', 'aoeuidhtns')

    def test_span_tags_with_chaining(self):
        span = self.tracer().start_manual(operation_name='Farnsworth')
        span. \
            set_tag('birthday', '9 April, 2841'). \
            set_tag('loves', 'different lengths of wires')
        span. \
            set_tag('unicode_val', u'non-ascii: \u200b'). \
            set_tag(u'unicode_key_\u200b', 'ascii val')
        span.finish()

    def test_span_logs(self):
        span = self.tracer().start_manual(operation_name='Fry')

        # Newer API
        span.log_kv(
            {'frozen.year': 1999, 'frozen.place': 'Cryogenics Labs'})
        span.log_kv(
            {'defrosted.year': 2999, 'defrosted.place': 'Cryogenics Labs'},
            time.time())

        # Older API
        span.\
            log_event('frozen', {'year': 1999, 'place': 'Cryogenics Labs'}). \
            log_event('defrosted', {'year': 2999}). \
            log_event('became his own grandfather', 1947)
        span.\
            log(event='frozen'). \
            log(payload={'year': 1999}). \
            log(timestamp=time.time(),
                event='frozen',
                payload={'year': 1999}). \
            log(timestamp=time.time(),
                event='unfrozen',
                payload={'year': 2999})

    def test_span_baggage(self):
        with self.tracer().start_manual(operation_name='Fry') as span:
            assert span.context.baggage == {}
            span_ref = span.set_baggage_item('Kiff-loves', 'Amy')
            assert span_ref is span
            val = span.get_baggage_item('Kiff-loves')
            if self.check_baggage_values():
                assert 'Amy' == val
            pass

    def test_context_baggage(self):
        with self.tracer().start_manual(operation_name='Fry') as span:
            assert span.context.baggage == {}
            span.set_baggage_item('Kiff-loves', 'Amy')
            if self.check_baggage_values():
                assert span.context.baggage == {'Kiff-loves': 'Amy'}
            pass

    def test_text_propagation(self):
        with self.tracer().start_manual(operation_name='Bender') as span:
            text_carrier = {}
            self.tracer().inject(
                span_context=span.context,
                format=opentracing.Format.TEXT_MAP,
                carrier=text_carrier)
            extracted_ctx = self.tracer().extract(
                format=opentracing.Format.TEXT_MAP,
                carrier=text_carrier)
            assert extracted_ctx.baggage == {}

    def test_binary_propagation(self):
        with self.tracer().start_manual(operation_name='Bender') as span:
            bin_carrier = bytearray()
            self.tracer().inject(
                span_context=span.context,
                format=opentracing.Format.BINARY,
                carrier=bin_carrier)
            extracted_ctx = self.tracer().extract(
                format=opentracing.Format.BINARY,
                carrier=bin_carrier)
            assert extracted_ctx.baggage == {}

    def test_mandatory_formats(self):
        formats = [
            (Format.TEXT_MAP, {}),
            (Format.HTTP_HEADERS, {}),
            (Format.BINARY, bytearray()),
        ]
        with self.tracer().start_manual(operation_name='Bender') as span:
            for fmt, carrier in formats:
                # expecting no exceptions
                span.tracer.inject(span.context, fmt, carrier)
                span.tracer.extract(fmt, carrier)

    def test_unknown_format(self):
        custom_format = 'kiss my shiny metal ...'
        with self.tracer().start_manual(operation_name='Bender') as span:
            with pytest.raises(opentracing.UnsupportedFormatException):
                span.tracer.inject(span.context, custom_format, {})
            with pytest.raises(opentracing.UnsupportedFormatException):
                span.tracer.extract(custom_format, {})

    def test_tracer_start_active_scope(self):
        # the Tracer ScopeManager should store the active Scope
        tracer = self.tracer()
        scope = tracer.start_active(operation_name='Fry')

        if self.check_scope_manager():
            assert tracer.scope_manager.active() == scope

        scope.close()

    def test_tracer_start_active_nesting(self):
        # when a Scope is closed, the previous one must be activated
        tracer = self.tracer()
        with tracer.start_active(operation_name='Fry') as parent:
            with tracer.start_active(operation_name='Fry'):
                pass

            if self.check_scope_manager():
                assert tracer.scope_manager.active() == parent

        if self.check_scope_manager():
            assert tracer.scope_manager.active() is None

    def test_tracer_start_active_nesting_finish_on_close(self):
        # finish_on_close must be correctly handled
        tracer = self.tracer()
        parent = tracer.start_active(operation_name='Fry',
                                     finish_on_close=False)
        with mock.patch.object(parent.span(), 'finish') as finish:
            with tracer.start_active(operation_name='Fry'):
                pass
            parent.close()

        assert finish.call_count == 0

        if self.check_scope_manager():
            assert tracer.scope_manager.active() is None

    def test_tracer_start_active_wrong_close_order(self):
        # only the active `Scope` can be closed
        tracer = self.tracer()
        parent = tracer.start_active(operation_name='Fry')
        child = tracer.start_active(operation_name='Fry')
        parent.close()

        if self.check_scope_manager():
            assert tracer.scope_manager.active() == child

    def test_tracer_start_manual_scope(self):
        # the Tracer ScopeManager should not store the new Span
        tracer = self.tracer()
        span = tracer.start_manual(operation_name='Fry')

        if self.check_scope_manager():
            assert tracer.scope_manager.active() is None

        span.finish()

    def test_tracer_scope_manager_active(self):
        # a `ScopeManager` has no scopes in its initial state
        tracer = self.tracer()

        if self.check_scope_manager():
            assert tracer.scope_manager.active() is None

    def test_tracer_scope_manager_activate(self):
        # a `ScopeManager` should activate any `Span`
        tracer = self.tracer()
        span = tracer.start_manual(operation_name='Fry')
        tracer.scope_manager.activate(span)

        if self.check_scope_manager():
            assert tracer.scope_manager.active().span() == span
