#!/usr/bin/env python

from __future__ import print_function

import sys
import apt_pkg
from peak_common import Peak

type_recommends = 4

if __name__ == '__main__':
    apt_pkg.init()

    try:
        if apt_pkg.VersionCompare(apt_pkg.VERSION, "0.8") < 0:
            print("Must use python-apt 0.8 or greater.", file=sys.stderr)
            sys.exit()
    except AttributeError:
        if apt_pkg.VERSION < "0.8":
            print("Must use python-apt 0.8 or greater.", file=sys.stderr)
            sys.exit()

    if apt_pkg.Dependency.TYPE_RECOMMENDS != type_recommends:
        print("PYTHON-APT BUG: apt_pkg.Dependency.TYPE_RECOMMENDS is not equal to 4", file=sys.stderr)

    cache = apt_pkg.Cache(None)

    test_pkg = cache[sys.argv[1]]
    peak = Peak(cache)
    peak.set_verbose(True)
    if peak.is_peak(test_pkg):
        print("Peak package.")
    else:
        print("Not peak package.")
