#!/usr/bin/env python

from __future__ import print_function

import sys
import apt_pkg

type_recommends = 4

class RevdependsCounter:

    def __init__(self, cache):
        self.cache = cache

    def count_pkg_revdepends(self, pkg, maxcount):
        self.maxcount = maxcount
        self.pkg_except = set()
        return self.count_pkg_revdepends_loop(pkg)

    def count_pkg_revdepends_except(self, pkg, maxcount, pkg_except):
        self.maxcount = maxcount
        self.pkg_except = pkg_except
        return self.count_pkg_revdepends_loop(pkg)

    def count_pkg_revdepends_loop(self, pkg):

        rev_depends = 0
        for otherdep in pkg.rev_depends_list:
            if otherdep.parent_pkg.current_ver != None and \
                    otherdep.parent_pkg.current_ver.id == otherdep.parent_ver.id and \
                    (otherdep.dep_type_enum == apt_pkg.Dependency.TYPE_DEPENDS or \
                    otherdep.dep_type_enum == apt_pkg.Dependency.TYPE_PREDEPENDS) and \
                    not otherdep.parent_pkg.id in self.pkg_except:
                rev_depends += 1
                if rev_depends >= self.maxcount:
                    return rev_depends
        if pkg.current_ver != None:
            for provided in pkg.current_ver.provides_list:
                try:
                    provides_pkg = self.cache[provided[0]]
                    if provides_pkg.current_ver == None:
                        rev_depends += self.count_pkg_revdepends_loop(provides_pkg)
                    if rev_depends >= self.maxcount:
                            return rev_depends
                except KeyError as e:
                    print("Package not found:", str(e).strip('"'))

        return rev_depends


def is_available(pkg):
    return pkg.has_provides or pkg.current_ver != None

class CirclelessRevdependsCounter:

    def __init__(self, rev_c):
        self.rev_c = rev_c

    def dependencies(self, pkg):

        if pkg.id in self.deps:
            return
        self.deps.add(pkg.id)

        if pkg.current_ver != None:
            for or_group in pkg.current_ver.depends_list.get("PreDepends", []) + \
                    pkg.current_ver.depends_list.get("Depends", []):
                for otherdep in or_group:
                    if is_available(otherdep.target_pkg) and \
                                    self.rev_c.count_pkg_revdepends_except(otherdep.target_pkg, 1, self.deps) == 0:
                        self.dependencies(otherdep.target_pkg)
        if pkg.has_provides:
            for provider in pkg.provides_list:
                if is_available(provider[2].parent_pkg):
                    self.dependencies(provider[2].parent_pkg)


    def count_pkg_revrecommends(self, pkg, maxcount):
            global type_recommends

            self.deps = set()
            self.dependencies(pkg)
            rev_recommends = 0
            for otherdep in pkg.rev_depends_list:
                if otherdep.parent_pkg.current_ver != None and \
                        otherdep.parent_pkg.current_ver.id == otherdep.parent_ver.id and \
                        otherdep.dep_type_enum == type_recommends and \
                        not otherdep.parent_pkg.id in self.deps:
                    rev_recommends += 1
                    if rev_recommends >= maxcount:
                        return rev_recommends
            return rev_recommends

def list_orphans(orphans, cache):

        rev_c = RevdependsCounter(cache)
        crev_c = CirclelessRevdependsCounter(rev_c)

        for otherpkg in cache.packages:
            if otherpkg.current_ver != None and not otherpkg.essential \
                                            and not otherpkg.important:
                if rev_c.count_pkg_revdepends(otherpkg, 1) == 0 and\
                        crev_c.count_pkg_revrecommends(otherpkg, 1) == 0:
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

    print("List of peak packages:", file=sys.stderr)
    orphans = list()
    list_orphans(orphans, cache)
    orphans.sort()
    print("\n".join(orphans))

