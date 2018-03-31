# Copyright (c) The OpenTracing Authors.
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

from opentracing.span import Span
from opentracing.ext.scope_manager import ThreadLocalScopeManager


def test_ext_scope_implicit_stack():
    scope_manager = ThreadLocalScopeManager()

    background_span = mock.MagicMock(spec=Span)
    foreground_span = mock.MagicMock(spec=Span)

    with scope_manager.activate(background_span, True) as background_scope:
        assert background_scope is not None

        # Activate a new Scope on top of the background one.
        with scope_manager.activate(foreground_span, True) as foreground_scope:
            assert foreground_scope is not None
            assert scope_manager.active is foreground_scope

        # And now the background_scope should be reinstated.
        assert scope_manager.active is background_scope

    assert background_span.finish.call_count == 1
    assert foreground_span.finish.call_count == 1

    assert scope_manager.active is None


def test_when_different_span_is_active():
    scope_manager = ThreadLocalScopeManager()

    span = mock.MagicMock(spec=Span)
    active = scope_manager.activate(span, False)
    scope_manager.activate(mock.MagicMock(spec=Span), False)
    active.close()

    assert span.finish.call_count == 0
