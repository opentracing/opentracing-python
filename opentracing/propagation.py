# Copyright (c) 2016 The OpenTracing Authors.
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


class UnsupportedFormatException(Exception):
    """UnsupportedFormatException should be used when the provided format
    value is unknown or disallowed by the Tracer.

    See Tracer.inject() and Tracer.join().
    """
    pass


class InvalidCarrierException(Exception):
    """InvalidCarrierException should be used when the provided carrier
    instance does not match what the `format` argument requires.

    See Tracer.inject() and Tracer.join().
    """
    pass


class TraceCorruptedException(Exception):
    """TraceCorruptedException should be used when the underlynig trace state
    is seemingly present but not well-formed.

    See Tracer.inject() and Tracer.join().
    """
    pass


class Format:
    """A namespace for builtin carrier formats.

    These static constants are intended for use in the Tracer.inject() and
    Tracer.join() methods. E.g.,

        tracer.inject(span, Format.BINARY, binary_carrier)

    """

    # The BINARY format injects Spans into and joins Spans from an opaque
    # bytearray carrier. For both Tracer.inject() and Tracer.join() the carrier
    # should be a bytearray instance. Tracer.inject() must append to the
    # bytearray carrier (rather than replace its contents).
    BINARY = 'binary'

    # The TEXT_MAP format injects Spans into and joins Spans from a python dict
    # carrier that maps from strings to strings.
    #
    # NOTE: Since HTTP headers are a particularly important use case for the
    # TEXT_MAP carrier, dict key parameters identify their respective values in
    # a case-insensitive manner.
    #
    # NOTE: The TEXT_MAP carrier dict may contain unrelated data (e.g.,
    # arbitrary HTTP headers). As such, the Tracer implementation should use a
    # prefix or other convention to distinguish Tracer-specific key:value
    # pairs.
    TEXT_MAP = 'text_map'
