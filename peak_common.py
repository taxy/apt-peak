#!/usr/bin/env python

from __future__ import print_function

import apt_pkg

type_recommends = 4

class RevdependsCounter:

    def __init__(self, cache):
        self.cache = cache
        self.removed = None

    def installed(self, pkg):
        return pkg.current_ver != None and (self.removed == None or not pkg.id in self.removed)

    def simulation_mode_on(self):
        self.removed = set()

    def simulated_remove(self, pkg):
        self.removed.add(pkg.id)

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
            if self.installed(otherdep.parent_pkg) and \
                    otherdep.parent_pkg.current_ver.id == otherdep.parent_ver.id and \
                    (otherdep.dep_type_enum == apt_pkg.Dependency.TYPE_DEPENDS or \
                    otherdep.dep_type_enum == apt_pkg.Dependency.TYPE_PREDEPENDS) and \
                    not otherdep.parent_pkg.id in self.pkg_except:
                rev_depends += 1
                if rev_depends >= self.maxcount:
                    return rev_depends
        if self.installed(pkg):
            for provided in pkg.current_ver.provides_list:
                try:
                    provides_pkg = self.cache[provided[0]]
                    if not self.installed(provides_pkg):
                        rev_depends += self.count_pkg_revdepends_loop(provides_pkg)
                    if rev_depends >= self.maxcount:
                            return rev_depends
                except KeyError as e:
                    print("Package not found:", str(e).strip('"'))

        return rev_depends

class CirclelessRevdependsCounter:

    def __init__(self, rev_c):
        self.rev_c = rev_c

    def is_available(self, pkg):
        return pkg.has_provides or self.rev_c.installed(pkg)

    def dependency_version(self, pkg):
        if self.rev_c.installed(pkg):
            for or_group in pkg.current_ver.depends_list.get("PreDepends", []) + \
                    pkg.current_ver.depends_list.get("Depends", []):
                for otherdep in or_group:
                    if self.is_available(otherdep.target_pkg) and \
                                    self.rev_c.count_pkg_revdepends_except(otherdep.target_pkg, 1, self.deps) == 0:
                        self.dependencies(otherdep.target_pkg)

    def dependency_provides(self, pkg):
        if pkg.has_provides:
            for provider in pkg.provides_list:
                if self.is_available(provider[2].parent_pkg):
                    self.dependency_version(provider[2].parent_pkg)

    def dependencies(self, pkg):
        if pkg.id in self.deps:
            return
        self.deps.add(pkg.id)

        self.dependency_version(pkg)
        self.dependency_provides(pkg)

    def count_pkg_revrecommends(self, pkg, maxcount):
            global type_recommends

            self.deps = set()
            self.dependencies(pkg)
            rev_recommends = 0
            for otherdep in pkg.rev_depends_list:
                if self.rev_c.installed(otherdep.parent_pkg) and \
                        otherdep.parent_pkg.current_ver.id == otherdep.parent_ver.id and \
                        otherdep.dep_type_enum == type_recommends and \
                        not otherdep.parent_pkg.id in self.deps:
                    rev_recommends += 1
                    if rev_recommends >= maxcount:
                        return rev_recommends
            return rev_recommends
