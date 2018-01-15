# Copyright (c) 2017 The OpenTracing Authors.
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

import logging
import threading
from ..tracer import Tracer


def get():
    """Returns the constant global tracer instance.
    All methods are forwarded to the currently configured tracer.
    Until a tracer is explicitly configured, no trace actually
    takes place.
    """
    return _GlobalTracer.tracer()


def register(tracer):
    """Registers a tracer to back the behaviour of the global tracer.
    Every application intending to use the global tracer is responsible
    for registering it once during its initialization.

        :param tracer: Tracer to use as global tracer.
    """
    _GlobalTracer.register(tracer)


def is_registered():
    return _GlobalTracer.is_registered()


class _GlobalTracer(Tracer):
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        super(_GlobalTracer, self).__init__()
        self._tracer = Tracer()

    @classmethod
    def reset(cls):
        cls._instance._tracer = Tracer()

    @classmethod
    def tracer(cls):
        return cls._instance

    @classmethod
    def register(cls, tracer):
        if tracer is None:
            raise ValueError('cannot register GlobalTracer <null>.')

        with cls._lock:
            if isinstance(tracer, _GlobalTracer):
                logging.warn('Attempted to register the GlobalTracer '
                             'as delegate of itself.')
                return

            global_tracer = cls._instance

            if type(global_tracer._tracer) is Tracer:
                global_tracer._tracer = tracer
            elif global_tracer._tracer is not tracer:
                raise ValueError('There is already a current global '
                                 'tracer registered.')

    @classmethod
    def is_registered(cls):
        with cls._lock:
            global_tracer = cls._instance
            return type(global_tracer._tracer) is not Tracer

    def start_span(self,
                   operation_name=None,
                   child_of=None,
                   references=None,
                   tags=None,
                   start_time=None):
        return self._tracer.start_span(operation_name,
                                       child_of,
                                       references,
                                       tags,
                                       start_time)

    def inject(self, span_context, format, carrier):
        return self._tracer.inject(span_context, format, carrier)

    def extract(self, format, carrier):
        return self._tracer.extract(format, carrier)

    def __str__(self):
        return 'GlobalTracer{0}'.format(self._tracer.__str__())


_GlobalTracer._instance = _GlobalTracer()
