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


class RawSpan(object):
    """
    Represents all accumulated state associated with a finished Span.
    """
    def __init__(self, trace_context, operation_name):
        self.trace_context = trace_context
        self.operation_name = operation_name
        self.start_time = None
        self.duration = None
        self.tags = None  # dictionary when initialized
        self.logs = None  # array of RawLog's when initialized

    def set_tag(self, key, value):
        if self.tags is None:
            self.tags = dict()
        self.tags[key] = value

    def add_log(self, log):
        if self.logs is None:
            self.logs = []
        self.logs.append(log)


class RawLog(object):
    """
    Encapsulates a log attached to a Span.
    """
    def __init__(self, timestamp, is_error, message, *args):
        self.timestamp = timestamp
        self.is_error = is_error
        self.message = message
        self.payload = args
