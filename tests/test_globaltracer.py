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
import mock
import opentracing


def test_opentracing_tracer():
    assert opentracing.tracer is opentracing.global_tracer()
    assert isinstance(opentracing.global_tracer(), opentracing.Tracer)


@mock.patch('opentracing.tracer')
def test_set_global_tracer(mock_obj):
    tracer = mock.Mock()
    opentracing.set_global_tracer(tracer)
    assert opentracing.global_tracer() is tracer

    opentracing.set_global_tracer(mock_obj)
    assert opentracing.global_tracer() is mock_obj


def test_register_none():
    with pytest.raises(ValueError):
        opentracing.set_global_tracer(None)


def test_is_global_tracer_registered_defaults_to_false():
    assert opentracing.is_global_tracer_registered() is False


def test_is_global_tracer_registered_returns_true_after_registering_a_tracer():
    tracer = mock.Mock()
    opentracing.set_global_tracer(tracer)
    assert opentracing.is_global_tracer_registered() is True
