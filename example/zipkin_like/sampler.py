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
import time

MAX_ID_BITS = 63

default_logger = logging.getLogger(__name__)


class Sampler(object):
    """
    Sampler is responsible for deciding if a particular span should be
    "sampled", i.e. recorded in permanent storage.
    """

    def is_sampled(self, trace_id):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()


class ConstSampler(Sampler):
    """
    ConstSampler always returns the same decision.
    """

    def __init__(self, decision):
        self.decision = decision

    def is_sampled(self, trace_id):
        return self.decision

    def close(self):
        pass

    def __str__(self):
        return 'ConstSampler(%s)' % self.decision


class ProbabilisticSampler(Sampler):
    """
    A sampler that randomly samples a certain percentage of traces specified
    by the samplingRate, in the range between 0.0 and 1.0.

    It relies on the fact that new trace IDs are 64bit random numbers
    themselves, thus making the sampling decision without generating a new
    random number, but simply calculating if traceID < (samplingRate * 2^64).
    Note that we actually ignore (zero out) the most significant bit.
    """

    def __init__(self, rate):
        assert 0.0 <= rate <= 1.0, "Sampling rate must be between 0.0 and 1.0"
        self.rate = rate
        self.max_number = 1 << MAX_ID_BITS
        self.boundary = rate * self.max_number

    def is_sampled(self, trace_id):
        return trace_id < self.boundary

    def close(self):
        pass

    def __str__(self):
        return 'ProbabilisticSampler(%s)' % self.rate


class RateLimitingSampler(Sampler):
    """
    Samples at most max_traces_per_second. The distribution of sampled
    traces follows burstiness of the service, i.e. a service with uniformly
    distributed requests will have those requests sampled uniformly as well,
    but if requests are bursty, especially sub-second, then a number of
    sequential requests can be sampled each second.
    """

    def __init__(self, max_traces_per_second=10):
        assert max_traces_per_second >= 0, \
            'max_traces_per_second must not be negative'
        self.credits_per_second = max_traces_per_second
        self.balance = max_traces_per_second
        self.last_tick = self.timestamp()
        self.item_cost = 1

    def is_sampled(self, trace_id):
        current_time = self.timestamp()
        elapsed_time = current_time - self.last_tick
        self.last_tick = current_time
        self.balance += elapsed_time * self.credits_per_second
        if self.balance > self.credits_per_second:
            self.balance = self.credits_per_second
        if self.balance >= self.item_cost:
            self.balance -= self.item_cost
            return True
        return False

    def close(self):
        pass

    @staticmethod
    def timestamp():
        return time.time()

    def __str__(self):
        return 'RateLimitingSampler(%s)' % self.credits_per_second
