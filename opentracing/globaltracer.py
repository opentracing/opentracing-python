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

from threading import Lock

from .tracer import Tracer


DEFAULT_TRACER = Tracer()


class GlobalTracer(Tracer):
    _tracer = DEFAULT_TRACER
    _tracer_lock = Lock()

    _instance = None  # assign it after the class has been fully declared.

    @staticmethod
    def get_tracer():
        return GlobalTracer._instance

    @staticmethod
    def init_tracer(tracer):
        if tracer is None:
            raise ValueError('tracer cannot be None')

        with GlobalTracer._tracer_lock:
            if GlobalTracer._tracer is not DEFAULT_TRACER:
                return False

            GlobalTracer._tracer = tracer
            return True

    @staticmethod
    def reset_tracer():
        with GlobalTracer._tracer_lock:
            GlobalTracer._tracer = DEFAULT_TRACER

    @property
    def scope_manager(self):
        return GlobalTracer._tracer.scope_manager

    @property
    def active_span(self):
        return GlobalTracer._tracer.active_span

    def start_active_span(self,
                          operation_name,
                          child_of=None,
                          references=None,
                          tags=None,
                          start_time=None,
                          ignore_active_span=False,
                          finish_on_close=True):
        return GlobalTracer._tracer.start_active_span(operation_name,
                                                      child_of,
                                                      references,
                                                      tags,
                                                      start_time,
                                                      ignore_active_span,
                                                      finish_on_close)

    def start_span(self,
                   operation_name=None,
                   child_of=None,
                   references=None,
                   tags=None,
                   start_time=None,
                   ignore_active_span=False):
        return GlobalTracer._tracer.start_span(operation_name,
                                               child_of,
                                               references,
                                               tags,
                                               start_time,
                                               ignore_active_span)

    def inject(self, span_context, format, carrier):
        return GlobalTracer._tracer.inject(span_context, format, carrier)

    def extract(self, format, carrier):
        return GlobalTracer._tracer.extract(format, carrier)

GlobalTracer._instance = GlobalTracer()

init_global_tracer = GlobalTracer.init_tracer
get_global_tracer = GlobalTracer.get_tracer
