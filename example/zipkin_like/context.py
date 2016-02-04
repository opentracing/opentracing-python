# Copyright (c) 2015 Uber Technologies, Inc.
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
import threading
import random
import time

import os
import opentracing.context

from .span import SAMPLED_FLAG, DEBUG_FLAG
from .sampler import MAX_ID_BITS

class BaseTraceContext(object):
    """Base implementation of opentracing.TraceContext.

    This implementation provides thread-safe Trace Attributes propagation
    methods, but does not have any notion of the span identity. It is meant
    for extension by the actual tracing implementations.
    """
    def __init__(self, trace_attributes=None):
        """Initializes this Trace Context with optional Trace Attributes.

        :param trace_attributes: string->string dictionary of Trace
            Attributes. Used as is, without copying, so the caller is
            expected to give ownership of this dictionary.
        :type trace_attributes: dict

        :return: None
        """
        self.trace_attributes = trace_attributes
        self.lock = Lock()

    def normalize_key(self, key):
        """Normalizes the key.

        The keys are always normalized before use by replacing underscores
        with dashes and converting the result to lowercase. For performance
        reasons, the complete validation of the key value to match the
        target regexp `(?i:[a-z0-9][-a-z0-9]*)` is not performed, it is up
        to the implementation to enforce this.

        :param key: some string key
        :return: normalized key
        """
        return key.replace('_', '-').lower()

    def set_trace_attribute(self, key, value):
        """Implements set_trace_attribute() of opentracing.TraceContext.

        :param key: string key
        :type key: str

        :param value: value of the attribute
        :type value: str

        :rtype : TraceContext
        :return: itself, for chaining the calls.
        """
        assert type(key) is str, 'key must be a string'
        assert type(value) is str, 'value must be a string'

        with self.lock:
            if self.trace_attributes is None:
                self.trace_attributes = dict()
            self.trace_attributes[self.normalize_key(key)] = value
        return self

    def get_trace_attribute(self, key):
        """Implements get_trace_attribute of :type:opentracing.TraceContext.

        :param key: string key
        :return: a Trace Attribute value, or None if no such key was stored.
        """
        with self.lock:
            if self.trace_attributes is None:
                return None
            else:
                return self.trace_attributes.get(self.normalize_key(key))

    def trace_attributes_as_dict(self):
        """Returns a copy of Trace Attributes.

        :return: copy of the Trace Attributes dictionary or None if no
            Trace Attributes was defined in this context.
        """
        with self.lock:
            if self.trace_attributes is None:
                out = None
            else:
                out = dict(self.trace_attributes)
        return out


class TraceContext(BaseTraceContext):
    """
    Zipkin-style subclass of standard TraceContext
    """

    def __init__(self, trace_id, span_id, parent_id, flags,
                 trace_attributes=None):
        """
        Constructor of a Trace Context.
        :param trace_id:
        :param span_id:
        :param parent_id:
        :param flags:
        :param trace_attributes: string->string dictionary of Trace Attributes.
            Used as is, without copying, so the caller is expected to give
            ownership of this dictionary.
        :return: new TraceContext
        """
        super(TraceContext, self).__init__(trace_attributes=trace_attributes)
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_id = parent_id
        self.flags = flags

    def span_id_as_tuple(self):
        """
        Method used in testing
        :return: returns a tuple (trace_id, span_id, parent_id, flags)
        """
        return self.trace_id, self.span_id, self.parent_id, self.flags

    def __str__(self):
        from .codecs import TraceContextEncoder

        return TraceContextEncoder.id_to_string(self)

    def append_trace_attributes(self, trace_attributes):
        """Adds extra Trace Attributes to the current context

        :param: extra Trace Attributes dictionary
        :return: None
        """
        with self.lock:
            if self.trace_attributes is None:
                self.trace_attributes = {}
            for key in trace_attributes.keys():
                norm_key = self.normalize_key(key)
                self.trace_attributes[norm_key] = trace_attributes[key]


class TraceContextSource(opentracing.context.TraceContextSource):
    """
    Zipkin-style TraceContextSource.
    """

    def __init__(self, sampler):
        self.sampler = sampler
        self.random = random.Random(time.time() * (os.getpid() or 1))
        self.sampler_lock = threading.Lock()

    def random_id(self):
        return self.random.getrandbits(MAX_ID_BITS)

    def new_root_trace_context(self, debug=False):
        with self.sampler_lock:
            trace_id = self.random_id()
            if debug:
                flags = SAMPLED_FLAG + DEBUG_FLAG
            elif self.sampler.is_sampled(trace_id):
                flags = SAMPLED_FLAG
            else:
                flags = 0
        return TraceContext(trace_id=trace_id, span_id=trace_id,
                            parent_id=None, flags=flags)

    def new_child_trace_context(self, parent_trace_context):
        trace_attributes = parent_trace_context.trace_attributes_as_dict()
        ctx = TraceContext(trace_id=parent_trace_context.trace_id,
                           span_id=self.random_id(),
                           parent_id=parent_trace_context.span_id,
                           flags=parent_trace_context.flags,
                           trace_attributes=trace_attributes)
        return ctx, None

    def close(self):
        self.sampler.close()
