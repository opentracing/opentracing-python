# Copyright The OpenTracing Authors
# Copyright Uber Technologies, Inc
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
from .span import Span  # noqa
from .span import SpanContext  # noqa
from .scope import Scope  # noqa
from .scope_manager import ScopeManager  # noqa
from .tracer import child_of  # noqa
from .tracer import follows_from  # noqa
from .tracer import Reference  # noqa
from .tracer import ReferenceType  # noqa
from .tracer import Tracer  # noqa
from .tracer import start_child_span  # noqa
from .propagation import Format  # noqa
from .propagation import InvalidCarrierException  # noqa
from .propagation import SpanContextCorruptedException  # noqa
from .propagation import UnsupportedFormatException  # noqa

# Global variable that should be initialized to an instance of real tracer.
# Note: it should be accessed via 'opentracing.tracer', not via
# 'from opentracing import tracer', the latter seems to take a copy.
tracer = Tracer()
