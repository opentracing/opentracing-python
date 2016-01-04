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

import sys
from concurrent.futures import Future
from tornado import gen, ioloop


def get_io_loop(channel):
    """
    Extracts IOLoop from TChannel instance, or tries to get the current one,
    but without starting a new one.
    :param channel:
    :return:
    """
    if hasattr(channel, '_threadloop') and \
            hasattr(channel._threadloop, '_io_loop'):
        return channel._threadloop._io_loop
    return ioloop.IOLoop.current(instance=False)


def submit(fn, io_loop, *args, **kwargs):
    """Submit Tornado Coroutine to IOLoop.current().

    :param fn: Tornado Coroutine to execute
    :param io_loop: Tornado IOLoop where to schedule the coroutine
    :param args: Args to pass to coroutine
    :param kwargs: Kwargs to pass to coroutine
    :returns concurrent.futures.Future: future result of coroutine
    """
    future = Future()

    def execute():
        """Executes fn on the IOLoop."""
        try:
            result = gen.maybe_future(fn(*args, **kwargs))
        except Exception:
            # The function we ran didn't return a future and instead raised
            # an exception. Let's pretend that it returned this dummy
            # future with our stack trace.
            f = gen.Future()
            f.set_exc_info(sys.exc_info())
            on_done(f)
        else:
            result.add_done_callback(on_done)

    def on_done(tornado_future):
        """Sets tornado.Future results to the concurrent.Future."""

        exception = tornado_future.exception()
        if not exception:
            future.set_result(tornado_future.result())
        else:
            future.set_exception(exception)

    io_loop.add_callback(execute)

    return future


def future_result(result):
    future = Future()
    future.set_result(result)
    return future


def future_exception(exception):
    future = Future()
    future.set_exception(exception)
    return future
