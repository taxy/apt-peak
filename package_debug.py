#!/usr/bin/env python

from __future__ import print_function

import sys
import apt_pkg
from peak_common import RevdependsCounter
from peak_common import CirclelessRevdependsCounter

type_recommends = 4

def list_orphans(orphans, cache):


        for otherpkg in cache.packages:
            if otherpkg.current_ver != None and not otherpkg.essential \
                                            and not otherpkg.important:
                    orphans.append(otherpkg.get_fullname(True))

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
    rev_c = RevdependsCounter(cache)
    rev_c.set_verbose(True)
    crev_c = CirclelessRevdependsCounter(rev_c)
    if rev_c.count_pkg_revdepends(test_pkg, 1) == 0 and\
            crev_c.count_pkg_revrecommends(test_pkg, 1) == 0:
        print("Peak package.")
    else:
        print("Not peak package.")
