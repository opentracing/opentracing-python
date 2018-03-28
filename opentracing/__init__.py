# Copyright The OpenTracing Authors
# Copyright Uber Technologies, Inc

from __future__ import absolute_import
from .span import Span  # noqa
from .span import SpanContext  # noqa
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
