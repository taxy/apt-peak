#!/usr/bin/env python

from __future__ import print_function

import sys
import apt_pkg
from optparse import OptionParser
from peak_common import RevdependsCounter
from peak_common import CirclelessRevdependsCounter

type_recommends = 4

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

def add_providers(target_pkg, related_ids, related_pkgs):
    if target_pkg.has_provides:
        for provider in pkg.provides_list:
            if not provider[2].parent_pkg.id in related_ids and\
                    provider[2].parent_pkg.current_ver != None and\
                    provider[2].parent_pkg.current_ver.id == provider[2].id:
                related_ids.add(provider[2].parent_pkg.id)
                related_pkgs.append(provider[2].parent_pkg)


def collect_all_related_pkgs(remove, related_pkgs):
    related_ids = set()
    for pkg in remove:
        if pkg.current_ver != None:
            for or_group in pkg.current_ver.depends_list.get("PreDepends", []) + \
                    pkg.current_ver.depends_list.get("Depends", []) + \
                    pkg.current_ver.depends_list.get("Recommends", []):
                for otherdep in or_group:
                    if not otherdep.target_pkg.id in related_ids:
                        if otherdep.target_pkg.current_ver != None:
                            related_ids.add(otherdep.target_pkg.id)
                            related_pkgs.append(otherdep.target_pkg)
                        else:
                            add_providers(otherdep.target_pkg, related_ids, related_pkgs)


def collect_is_peak(related_pkgs, removable_ids, rev_c, crev_c, remove):
    for otherpkg in related_pkgs:
        if not otherpkg.id in removable_ids and\
                rev_c.count_pkg_revdepends(otherpkg, 1) == 0 and\
                crev_c.count_pkg_revrecommends(otherpkg, 1) == 0:
            remove.append(otherpkg)


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

    removable = list()
    removable_ids = set()
    for pkg in remove:
        rev_c.simulated_remove(pkg)
        removable_ids.add(pkg.id)
        removable.append(pkg.get_fullname(True))

    related_pkgs = list()

    while len(remove) > 0:
        collect_all_related_pkgs(remove, related_pkgs)
        del remove[:]
        collect_is_peak(related_pkgs, removable_ids, rev_c, crev_c, remove)
        del related_pkgs[:]
        for pkg in remove:
            rev_c.simulated_remove(pkg)
            removable_ids.add(pkg.id)
            removable.append(pkg.get_fullname(True))

    print("List of removable packages:", file=sys.stderr)
    print(" ".join(removable))
