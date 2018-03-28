# Copyright The OpenTracing Authors

from __future__ import absolute_import


class UnsupportedFormatException(Exception):
    """UnsupportedFormatException should be used when the provided format
    value is unknown or disallowed by the Tracer.

    See Tracer.inject() and Tracer.extract().
    """
    pass


class InvalidCarrierException(Exception):
    """InvalidCarrierException should be used when the provided carrier
    instance does not match what the `format` argument requires.

    See Tracer.inject() and Tracer.extract().
    """
    pass


class SpanContextCorruptedException(Exception):
    """SpanContextCorruptedException should be used when the underlying span
    context state is seemingly present but not well-formed.

    See Tracer.inject() and Tracer.extract().
    """
    pass


class Format(object):
    """A namespace for builtin carrier formats.

    These static constants are intended for use in the Tracer.inject() and
    Tracer.extract() methods. E.g.::

        tracer.inject(span.context, Format.BINARY, binary_carrier)

    """

    BINARY = 'binary'
    """
    The BINARY format represents SpanContexts in an opaque bytearray carrier.

    For both Tracer.inject() and Tracer.extract() the carrier should be a
    bytearray instance. Tracer.inject() must append to the bytearray carrier
    (rather than replace its contents).
    """

    TEXT_MAP = 'text_map'
    """
    The TEXT_MAP format represents SpanContexts in a python dict mapping from
    strings to strings.

    Both the keys and the values have unrestricted character sets (unlike the
    HTTP_HEADERS format).

    NOTE: The TEXT_MAP carrier dict may contain unrelated data (e.g.,
    arbitrary gRPC metadata). As such, the Tracer implementation should use a
    prefix or other convention to distinguish Tracer-specific key:value
    pairs.
    """

    HTTP_HEADERS = 'http_headers'
    """
    The HTTP_HEADERS format represents SpanContexts in a python dict mapping
    from character-restricted strings to strings.

    Keys and values in the HTTP_HEADERS carrier must be suitable for use as
    HTTP headers (without modification or further escaping). That is, the
    keys have a greatly restricted character set, casing for the keys may not
    be preserved by various intermediaries, and the values should be
    URL-escaped.

    NOTE: The HTTP_HEADERS carrier dict may contain unrelated data (e.g.,
    arbitrary gRPC metadata). As such, the Tracer implementation should use a
    prefix or other convention to distinguish Tracer-specific key:value
    pairs.
    """
