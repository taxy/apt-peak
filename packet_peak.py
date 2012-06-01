#!/usr/bin/env python

from __future__ import print_function

import sys
import apt_pkg

cache = None
type_recommends = 4

class RevdependsCounter:

    def count_pkg_revdepends(self, pkg, maxcount):
        self.revdeps = set()
        self.maxcount = maxcount
        self.pkg_except = set()
        return self.count_pkg_revdepends_loop(pkg)

    def count_pkg_revdepends_except(self, pkg, maxcount, pkg_except):
        self.revdeps = set()
        self.maxcount = maxcount
        self.pkg_except = pkg_except
        return self.count_pkg_revdepends_loop(pkg)

    def count_pkg_revdepends_loop(self, pkg):
        global cache

        rev_depends = 0
        for otherdep in pkg.rev_depends_list:
            if otherdep.parent_pkg.current_ver != None and \
                    otherdep.parent_pkg.current_ver.id == otherdep.parent_ver.id and \
                    (otherdep.dep_type_enum == apt_pkg.Dependency.TYPE_DEPENDS or \
                    otherdep.dep_type_enum == apt_pkg.Dependency.TYPE_PREDEPENDS) and \
                    not otherdep.parent_pkg.id in self.pkg_except:
                if not otherdep.parent_pkg.id in self.revdeps:
                    self.revdeps.add(otherdep.parent_pkg.id)
                    rev_depends += 1
                if rev_depends >= self.maxcount:
                    return rev_depends
        if pkg.current_ver != None:
            for provided in pkg.current_ver.provides_list:
                try:
                    provides_pkg = cache[provided[0]]
                    if not provides_pkg.id in self.revdeps:
                        self.revdeps.add(provides_pkg.id)
                        if provides_pkg.current_ver != None and \
                                not provides_pkg.id in self.pkg_except:
                            rev_depends += 1
                        if not provides_pkg.has_versions:
                            rev_depends += self.count_pkg_revdepends_loop(provides_pkg)
                    if rev_depends >= self.maxcount:
                            return rev_depends
                except KeyError as e:
                    print("Package not found:", str(e).strip('"'))

        return rev_depends

rev_c = RevdependsCounter()

def is_available(pkg):
    return not (pkg.has_versions and pkg.current_ver == None)

class CirclelessRevdependsCounter:

    def dependencies(self, pkg):
        global rev_c

        if pkg.id in self.deps:
            return
        self.deps.add(pkg.id)

        if pkg.current_ver != None:
            for or_group in pkg.current_ver.depends_list.get("PreDepends", []) + \
                    pkg.current_ver.depends_list.get("Depends", []):
                for otherdep in or_group:
                    if is_available(otherdep.target_pkg) and \
                                    rev_c.count_pkg_revdepends_except(otherdep.target_pkg, 1, self.deps) == 0:
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

def list_orphans(orphans):
        global cache
        global rev_c
        crev_c = CirclelessRevdependsCounter()

        for otherpkg in cache.packages:
            if otherpkg.current_ver != None and not otherpkg.essential \
                                            and not otherpkg.important:
                if rev_c.count_pkg_revdepends(otherpkg, 1) == 0 and\
                        crev_c.count_pkg_revrecommends(otherpkg, 1) == 0:
                    orphans.append(otherpkg.name)

if __name__ == '__main__':
    apt_pkg.init()

    try:
        if apt_pkg.VersionCompare(apt_pkg.VERSION, "0.8") < 0:
            print("Must use python-apt 0.8 or greater.")
            sys.exit()
    except AttributeError:
        if apt_pkg.VERSION < "0.8":
            print("Must use python-apt 0.8 or greater.")
            sys.exit()

    if apt_pkg.Dependency.TYPE_RECOMMENDS != type_recommends:
        print("PYTHON-APT BUG: apt_pkg.Dependency.TYPE_RECOMMENDS is not equal to 4")

    cache = apt_pkg.Cache()

    print("List of orphan packages:")
    orphans = list()
    list_orphans(orphans)
    orphans.sort()
    print("\n".join(orphans))

