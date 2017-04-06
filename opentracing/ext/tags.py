# Copyright (c) 2016 The OpenTracing Authors.
#
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

# The following tags are described in greater detail at the following url:
# https://github.com/opentracing/specification/blob/master/semantic_conventions.md

# Here we define standard names for tags that can be added to spans by the
# instrumentation code. The actual tracing systems are not required to
# retain these as tags in the stored spans if they have other means of
# representing the same data. For example, the SPAN_KIND='server' can be
# inferred from a Zipkin span by the presence of ss/sr annotations.

# ---------------------------------------------------------------------------
# SPAN_KIND hints at relationship between spans, e.g. client/server
# ---------------------------------------------------------------------------
SPAN_KIND = 'span.kind'

# Marks a span representing the client-side of an RPC or other remote call
SPAN_KIND_RPC_CLIENT = 'client'

# Marks a span representing the server-side of an RPC or other remote call
SPAN_KIND_RPC_SERVER = 'server'

# ---------------------------------------------------------------------------
# ERROR indicates whether a Span ended in an error state.
# ---------------------------------------------------------------------------
ERROR = 'error'

# ---------------------------------------------------------------------------
# COMPONENT (string) ia s low-cardinality identifier of the module, library,
# or package that is generating a span.
# ---------------------------------------------------------------------------
COMPONENT = 'component'

# ---------------------------------------------------------------------------
# SAMPLING_PRIORITY (uint16) determines the priority of sampling this Span.
# ---------------------------------------------------------------------------
SAMPLING_PRIORITY = 'sampling.priority'

# ---------------------------------------------------------------------------
# PEER_* tags can be emitted by either client-side of server-side to describe
# the other side/service in a peer-to-peer communications, like an RPC call.
# ---------------------------------------------------------------------------

# PEER_SERVICE (string) records the service name of the peer
PEER_SERVICE = 'peer.service'

# PEER_HOSTNAME (string) records the host name of the peer
PEER_HOSTNAME = 'peer.hostname'

# PEER_ADDRESS (string) suitable for use in a networking client library.
# This may be a "ip:port", a bare "hostname", a FQDN, or even a
# JDBC substring like "mysql://prod-db:3306"
PEER_ADDRESS = 'peer.address'

# PEER_HOST_IPV4 (uint32) records IP v4 host address of the peer
PEER_HOST_IPV4 = 'peer.ipv4'

# PEER_HOST_IPV6 (string) records IP v6 host address of the peer
PEER_HOST_IPV6 = 'peer.ipv6'

# PEER_PORT (uint16) records port number of the peer
PEER_PORT = 'peer.port'

# ---------------------------------------------------------------------------
# HTTP tags
# ---------------------------------------------------------------------------

# HTTP_URL (string) should be the URL of the request being handled in this
# segment of the trace, in standard URI format. The protocol is optional.
HTTP_URL = 'http.url'

# HTTP_METHOD (string) is the HTTP method of the request.
# Both upper/lower case values are allowed.
HTTP_METHOD = 'http.method'

# HTTP_STATUS_CODE (int) is the numeric HTTP status code (200, 404, etc)
# of the HTTP response.
HTTP_STATUS_CODE = 'http.status_code'

# ---------------------------------------------------------------------------
# DATABASE tags
# ---------------------------------------------------------------------------

# DATABASE_INSTANCE (string) The database instance name. E.g., In java, if
# the jdbc.url="jdbc:mysql://127.0.0.1:3306/customers", the instance
# name is "customers"
DATABASE_INSTANCE = 'db.instance'

# DATABASE_STATEMENT (string) A database statement for the given database
# type. E.g., for db.type="SQL", "SELECT * FROM user_table";
# for db.type="redis", "SET mykey 'WuValue'".
DATABASE_STATEMENT = 'db.statement'

# DATABASE_TYPE (string) For any SQL database, "sql". For others,
# the lower-case database category, e.g. "cassandra", "hbase", or "redis".
DATABASE_TYPE = 'db.type'

# DATABASE_USER (string) Username for accessing database. E.g.,
# "readonly_user" or "reporting_user"
DATABASE_USER = 'db.user'

# ---------------------------------------------------------------------------
# MESSAGE_BUS tags
# ---------------------------------------------------------------------------

# MESSAGE_BUS_DESTINATION (string) An address at which messages can be
# exchanged. E.g. A Kafka record has an associated "topic name" that can
# be extracted by the instrumented producer or consumer and stored
# using this tag.
MESSAGE_BUS_DESTINATION = 'message_bus.destination'
