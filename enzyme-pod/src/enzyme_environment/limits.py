"""Fresh single-threaded child sets only its own limits, then execs bubblewrap."""
import os
import resource
import sys

os.nice(10)
os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:2])
for name, value in ((resource.RLIMIT_CORE, 0), (resource.RLIMIT_AS, 2 * 1024 ** 3),
                    (resource.RLIMIT_FSIZE, 8 * 1024 ** 2), (resource.RLIMIT_NOFILE, 128)):
    resource.setrlimit(name, (value, value))
resource.setrlimit(resource.RLIMIT_CPU, (100, 105))
os.execv(sys.argv[1], sys.argv[1:])
