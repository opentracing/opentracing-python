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
import time


class APICompatibilityCheckMixin(object):
    """
    A mixin class for validation that a given tracer implementation
    satisfies the requirements of the OpenTracing API.
    """

    def tracer(self):
        raise NotImplementedError('Subclass must implement tracer()')

    def check_trace_attribute_values(self):
        """If true, the test will validate trace attributes by
        storing and retrieving them from the trace context. If false,
        it will only attempt to store and retrieve the attributes to check
        the API compliance, but not actually validate stored values.
        The latter mode is only useful for no-op tracer.
        """
        return True

    def test_start_span(self):
        tracer = self.tracer()
        span = tracer.start_span(operation_name='Fry')
        span.finish()
        with tracer.start_span(operation_name='Fry',
                                tags={'birthday': 'August 14 1974'}) as span:
            span.log_event('birthplace',
                           payload={'hospital': 'Brooklyn Pre-Med Hospital',
                                    'city': 'Old New York'})
        tracer.flush()

    def test_start_span_with_parent(self):
        tracer = self.tracer()
        parent_span = tracer.start_span(operation_name='parent')
        assert parent_span is not None
        span = tracer.start_span(operation_name='Leela',
                                 parent=parent_span)
        span.finish()
        span = tracer.start_span(operation_name='Leela',
                                 parent=parent_span,
                                 tags={'birthplace': 'sewers'})
        span.finish()
        tracer.flush()

    def test_set_operation_name(self):
        span = self.tracer().start_span().set_operation_name('Farnsworth')
        span.finish()

    def test_span_as_context_manager(self):
        finish = {'called': False}

        def mock_finish(*_):
            finish['called'] = True

        with self.tracer().start_span(operation_name='antiquing') as span:
            setattr(span, 'finish', mock_finish)
        assert finish['called'] is True

        # now try with exception
        finish['called'] = False
        try:
            with self.tracer().start_span(operation_name='antiquing') as span:
                setattr(span, 'finish', mock_finish)
                raise ValueError()
        except ValueError:
            assert finish['called'] is True
        else:
            raise AssertionError('Expected ValueError')  # pragma: no cover

    def test_span_tags_with_chaining(self):
        span = self.tracer().start_span(operation_name='Farnsworth')
        span. \
            set_tag('birthday', '9 April, 2841'). \
            set_tag('loves', 'different lengths of wires')
        span.finish()

    def test_span_logs(self):
        span = self.tracer().start_span(operation_name='Fry')
        span.\
            log_event('frozen', {'year': 1999, 'place': 'Cryogenics Labs'}). \
            log_event('defrosted', {'year': 2999}). \
            log_event('became his own grandfather', 1947)
        span.\
            log(timestamp=time.time(),
                event='frozen',
                payload={'year': 1999}). \
            log(timestamp=time.time(),
                event='unfrozen',
                payload={'year': 2999})

    def test_trace_attributes(self):
        with self.tracer().start_span(operation_name='Fry') as span:
            span.set_trace_attribute('Kiff-loves', 'Amy')
            val = span.get_trace_attribute('kiff-Loves')  # case change
            if self.check_trace_attribute_values():
                assert 'Amy' == val
            pass

    def test_text_propagation(self):
        with self.tracer().start_span(operation_name='Bender') as span:
            dict_tracer_state, dict_attrs = self.tracer(). \
                propagate_span_as_text(span=span)
            assert type(dict_tracer_state) is dict
            assert dict_attrs is None or type(dict_attrs) is dict
            with self.tracer().join_trace_from_text(
                None,
                tracer_state=dict_tracer_state,
                trace_attributes=dict_attrs
            ) as reassembled_span:
                reassembled_span.set_trace_attribute(
                    'middle-name', 'Rodriguez')

    def test_binary_propagation(self):
        with self.tracer().start_span(operation_name='Bender') as span:
            bin_tracer_state, bin_attrs = self.tracer(). \
                propagate_span_as_binary(span=span)
            assert type(bin_tracer_state) is bytearray
            assert bin_attrs is None or type(bin_attrs) is bytearray
            with self.tracer().join_trace_from_binary(
                None,
                tracer_state=bin_tracer_state,
                trace_attributes=bin_attrs
            ) as reassembled_span:
                reassembled_span.set_trace_attribute(
                    'middle-name', 'Rodriguez')
