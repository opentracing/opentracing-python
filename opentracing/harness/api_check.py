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

    def test_start_trace(self):
        tracer = self.tracer()
        span = tracer.start_trace(operation_name='Fry')
        span.finish()
        with tracer.start_trace(operation_name='Fry',
                                tags={'birthday': 'August 14 1974'}) as span:
            span.info('birthplace',
                      {'hospital': 'Brooklyn Pre-Med Hospital',
                       'city': 'Old New York'})
        tracer.close()

    def test_join_trace(self):
        tracer = self.tracer()
        trace_context = tracer.new_root_trace_context()
        assert trace_context is not None
        span = tracer.join_trace(operation_name='Leela',
                                 parent_trace_context=trace_context)
        span.finish()
        span = tracer.join_trace(operation_name='Leela',
                                 parent_trace_context=trace_context,
                                 tags={'birthplace': 'sewers'})
        span.finish()
        tracer.close()

    def test_child_span(self):
        parent = self.tracer().start_trace(operation_name='Farnsworth')
        with parent as p:
            child = p.start_child(operation_name='Cubert')
            child.finish()

    def test_span_as_context_manager(self):
        finish = {'called': False}

        def mock_finish(*_):
            finish['called'] = True

        with self.tracer().start_trace(operation_name='antiquing') as span:
            setattr(span, 'finish', mock_finish)
        assert finish['called'] is True

        # now try with exception
        finish['called'] = False
        try:
            with self.tracer().start_trace(operation_name='antiquing') as span:
                setattr(span, 'finish', mock_finish)
                raise ValueError()
        except ValueError:
            assert finish['called'] is True
        else:
            raise AssertionError('Expected ValueError')  # pragma: no cover

    def test_span_tags(self):
        span = self.tracer().start_trace(operation_name='Farnsworth')
        span.add_tag('birthday', '9 April, 2841')
        span.add_tag('loves', 'different lengths of wires')
        span.finish()

    def test_span_logs(self):
        span = self.tracer().start_trace(operation_name='Fry')
        span.info('frozen', {'year': 1999, 'place': 'Cryogenics Labs'})
        span.error('defrosted', {'year': 2999})

    def test_trace_attributes(self):
        trace_context = self.tracer().new_root_trace_context()
        trace_context.set_trace_attribute('Kiff-loves', 'Amy')
        val = trace_context.get_trace_attribute('kiff-Loves')  # case change
        if self.check_trace_attribute_values():
            assert 'Amy' == val

    def test_trace_context_source_child(self):
        trace_context = self.tracer().new_root_trace_context()
        child_context, tags = self.tracer().new_child_trace_context(
            parent_trace_context=trace_context
        )
        child_context.set_trace_attribute('child', 'Igner')
        assert tags is None or type(tags) is dict

    def test_text_codecs(self):
        span = self.tracer().start_trace(operation_name='Bender')
        trace_context = span.trace_context
        dict_trace_id, dict_attrs = self.tracer().trace_context_to_text(
            trace_context=trace_context
        )
        assert type(dict_trace_id) is dict
        assert dict_attrs is None or type(dict_attrs) is dict
        trace_context = self.tracer().trace_context_from_text(
            trace_context_id=dict_trace_id,
            trace_attributes=dict_attrs
        )
        trace_context.set_trace_attribute('middle-name', 'Rodriguez')

    def test_binary_codecs(self):
        span = self.tracer().start_trace(operation_name='Bender')
        trace_context = span.trace_context
        bin_trace_id, bin_attrs = self.tracer().trace_context_to_binary(
            trace_context=trace_context
        )
        assert type(bin_trace_id) is bytearray
        assert bin_attrs is None or type(bin_attrs) is bytearray
        trace_context = self.tracer().trace_context_from_binary(
            trace_context_id=bin_trace_id,
            trace_attributes=bin_attrs
        )
        trace_context.set_trace_attribute('middle-name', 'Rodriguez')
