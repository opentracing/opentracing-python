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

# Here we define standard names for tags that can be handled specially by
# the tracing systems.

# PeerXXX tags can be emitted by either client-side of server-side to describe
# the other side/service in a peer-to-peer communications, like an RPC call.

# PeerService records the service name of the peer
PEER_SERVICE = 'peer.service'

# PeerHostname records the host name of the peer
PEER_HOSTNAME = 'peer.hostname'

# PeerHostIPv4 records IP v4 host address of the peer
PEER_HOST_IPV4 = 'peer.ipv4'

# PeerHostIPv6 records IP v6 host address of the peer
PEER_HOST_IPV6 = 'peer.ipv6'

# PeerPort records port number of the peer
PEER_PORT = 'peer.port'
