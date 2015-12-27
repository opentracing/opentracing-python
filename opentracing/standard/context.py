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
from threading import Lock
import opentracing


class TraceContext(opentracing.TraceContext):
    """Base implementation of opentracing.TraceContext.

    This implementation provides thread-safe metadata propagation methods,
    but does not have any notion of the span identity. It is meant for
    extension by the actual tracing implementations.

    Access to me
    """
    def __init__(self, metadata=None):
        """Initializes this trace context with optional metadata.

        :param metadata: string->string dictionary of metadata. Used as is,
            without copying, so the caller is expected to give ownership of
            this dictionary.
        :type metadata: dict

        :return: None
        """
        self.metadata = metadata
        self.lock = Lock()

    def normalize_key(self, key):
        """Normalizes the key.

        The keys are always normalized before use by replacing underscores
        with dashes and converting the result to lowercase. For performance
        reasons, the complete validation of the key value to match the
        target rexexp `(?i:[a-z0-9][-a-z0-9]*)` is not performed, it is up
        to the implementation to enforce this.

        :param key: some string key
        :return: normalized key
        """
        return key.replace('_', '-').lower()

    def set_metadata(self, key, value):
        """Implements set_metadata() of opentracing.TraceContext.

        :param key: string key
        :type key: str

        :param value: value of the metadata
        :type value: str

        :rtype : TraceContext
        :return: itself, for chaining the calls.
        """
        assert type(key) is str, 'key must be a string'
        assert type(value) is str, 'value must be a string'

        with self.lock:
            if self.metadata is None:
                self.metadata = dict()
            self.metadata[self.normalize_key(key)] = value
        return self

    def get_metadata(self, key):
        """Implements get_metadata of :type:opentracing.TraceContext.

        :param key: string key
        :return: a metadata value, or None if no such key was stored.
        """
        with self.lock:
            if self.metadata is None:
                return None
            else:
                return self.metadata.get(self.normalize_key(key))

    def metadata_as_dict(self):
        """Returns metadata as a cloned dictionary.

        :return: copy of the metadata dictionary or None if no metadata was
            defined in this context.
        """
        with self.lock:
            if self.metadata is None:
                out = None
            else:
                out = dict(self.metadata)
        return out
