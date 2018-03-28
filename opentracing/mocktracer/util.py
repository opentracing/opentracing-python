# Copyright (c) 2018 The OpenTracing Authors.
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

import random
import os
import time

# A mocktracer-specific instance of guid_rng. See _fork_guard_pid.
guid_rng = random.Random()

# The current pid. If the process forks (which happens, for instance, in
# uwsgi), we consult _fork_guard_pid and re-seed guid_rng accordingly.
_fork_guard_pid = 0


def generate_id():
    global _fork_guard_pid

    # Microbenchmarks suggest that os.getpid() takes less than 0.1 microsecond.
    pid = os.getpid()
    if (_fork_guard_pid == 0) or (_fork_guard_pid != pid):
        _fork_guard_pid = pid
        guid_rng.seed(int(1000000 * time.time()) ^ pid)
    return guid_rng.getrandbits(64) - 1
