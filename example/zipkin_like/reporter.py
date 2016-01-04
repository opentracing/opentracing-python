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
import logging

from concurrent.futures import Future
from . import ioloop_util, thrift

default_logger = logging.getLogger(__name__)


class NullReporter(object):
    """
    Ignores all spans
    """
    def report_span(self, span):
        pass

    def close(self):
        fut = Future()
        fut.set_result(True)
        return fut


class LoggingReporter(NullReporter):
    """
    Logs all spans
    """
    def __init__(self, logger=None):
        self.logger = logger if logger else default_logger

    def report_span(self, span):
        self.logger.warn('Reporting span %s', span)


class CompositeReporter(NullReporter):
    """
    Delegates reporting to one or more underlying reporters.
    """
    def __init__(self, *reporters):
        self.reporters = reporters

    def report_span(self, span):
        for reporter in self.reporters:
            reporter.report_span(span)

    def close(self):
        from threading import Lock
        lock = Lock()
        count = [0]
        future = Future()

        def on_close(_):
            with lock:
                count[0] += 1
                if count[0] == len(self.reporters):
                    future.set_result(True)

        for reporter in self.reporters:
            f = reporter.close()
            f.add_done_callback(on_close)

        return future


class ZipkinReporter(NullReporter):
    """
    Receives completed spans from Tracer and submits them to Collector.
    """

    def __init__(self, channel, buffer_size=10, flush_interval=0,
                 io_loop=None, **kwargs):
        from tornado.ioloop import PeriodicCallback
        from threading import Lock

        self._channel = channel
        self.buffer_size = buffer_size
        self.io_loop = io_loop
        self.logger = kwargs.get('logger', default_logger)

        if self.io_loop is None:
            self.io_loop = ioloop_util.get_io_loop(channel)
        self.io_loop_error_log = False
        self.spans = []
        self.spans_lock = Lock()
        if self.io_loop and flush_interval > 0:
            self.periodic = PeriodicCallback(callback=self.flush,
                                             callback_time=flush_interval*1000,  # to milliseconds
                                             io_loop=io_loop)
            self.periodic.start()
        else:
            self.periodic = None

    def report_span(self, span):
        with self.spans_lock:
            self.spans.append(span)
            size = len(self.spans)
        if size >= self.buffer_size:
            self.flush()

    def close(self):
        if self.periodic:
            self.periodic.stop()
        return self.flush()

    def flush(self):
        if self.io_loop is None:
            if not self.io_loop_error_log:
                self.logger.error('Reporter has no IOLoop')
                self.io_loop_error_log = True
                return ioloop_util.future_result(False)
        return ioloop_util.submit(self._flush, io_loop=self.io_loop)

    def _flush(self):

        def submit_callback(future):
            ex = future.exception()
            if ex:
                self.logger.error(
                    'Failed to submit trace to Collector: %s', ex)

        with self.spans_lock:
            spans = self.spans
            self.spans = []
        if len(spans) > 0:
            try:
                request = thrift.make_submit_batch_request(spans)
                fut = self._channel.thrift(request)
                fut.add_done_callback(submit_callback)
                return fut
            except Exception as e:
                self.logger.error('Failed to submit trace to tcollector: %s', e)
                return ioloop_util.future_exception(e)
        return ioloop_util.future_result(True)
