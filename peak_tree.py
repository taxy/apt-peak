#!/usr/bin/env python

from __future__ import print_function

import sys
import apt_pkg
from optparse import OptionParser
from peak_common import RevdependsCounter
from peak_common import CirclelessRevdependsCounter

type_recommends = 4

def list_orphans(orphans, cache):


        for otherpkg in cache.packages:
            if otherpkg.current_ver != None and not otherpkg.essential \
                                            and not otherpkg.important:
                if rev_c.count_pkg_revdepends(otherpkg, 1) == 0 and\
                        crev_c.count_pkg_revrecommends(otherpkg, 1) == 0:
                    orphans.append(otherpkg.get_fullname(True))

def dump(obj):
  for attr in dir(obj):
      print("obj.%s = %s" % (attr, getattr(obj, attr)))

def multi_arg(option, opt_str, value, parser):
    if getattr(parser.values, option.dest) == None:
        setattr(parser.values, option.dest, list())
    while len(parser.rargs) > 0 and parser.rargs[0][0] != '-':
        getattr(parser.values, option.dest).append(parser.rargs.pop(0))

def identify_packages(pkg_names, cache, pkgs):
    for pkg_name in pkg_names:
        try:
            pkgs.append(cache[pkg_name])
        except KeyError as e:
            print("Package not found:", str(e).strip('"'))


def packages_parse(argv, cache, remove, keep):
    parser = OptionParser(usage="Usage: %prog -r package_list [-k package_list]")
    parser.add_option("-r", "--remove", action="callback", callback=multi_arg,
                    dest='remove', help="Set removable peak packets")
    parser.add_option("-k", "--keep", action="callback", callback=multi_arg,
                    dest='keep', help="Set keepable dependency packets")
    options, args = parser.parse_args()
    if options.remove != None and len(options.remove) > 0:
        identify_packages(options.remove, cache, remove)
    else:
        print("error: Must set remove argument.\n", file=sys.stderr)
        parser.print_help(file=sys.stderr)
        sys.exit()

    if options.keep != None:
        identify_packages(options.keep, cache, keep)

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

    remove = list()
    keep = list()
    packages_parse(sys.argv[1:], cache, remove, keep)
    rev_c = RevdependsCounter(cache)
    rev_c.simulation_mode_on()
    crev_c = CirclelessRevdependsCounter(rev_c)

#    print("List of peak packages:", file=sys.stderr)
#    orphans = list()
#    list_orphans(orphans, cache)
#    orphans.sort()
#    print("\n".join(orphans))
