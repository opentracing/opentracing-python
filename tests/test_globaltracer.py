# Copyright The OpenTracing Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
import pytest
import opentracing
from opentracing.mocktracer import MockTracer
from opentracing.globaltracer import GlobalTracer


def test_singleton_reference():
    assert isinstance(opentracing.tracer, GlobalTracer)
    assert opentracing.tracer is opentracing.get_global_tracer()


def test_multiple_registrations():
    assert opentracing.init_global_tracer(MockTracer()) is True
    assert opentracing.init_global_tracer(MockTracer()) is False


def test_register_none():
    with pytest.raises(ValueError):
        opentracing.init_global_tracer(None)
