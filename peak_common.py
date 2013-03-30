#!/usr/bin/env python

from __future__ import print_function

import apt_pkg

type_recommends = 4

class Peak:

    def __init__(self, cache):
        self.cache = cache
        self.removed = None
        self.verbose = False
        self.verboseprint = lambda *a, **k: None
        self.records = apt_pkg.PackageRecords(cache)

    def set_verbose(self, verbose):
        self.verbose = verbose
        self.set_verboseprint(verbose)

    def set_verboseprint(self, verbose):
        self.verboseprint = print if verbose else lambda *a, **k: None

    def installed(self, pkg):
        return pkg.current_ver != None and (self.removed == None or not pkg.id in self.removed)

    def simulation_mode_on(self):
        self.removed = set()

    def simulated_remove(self, pkg):
        self.removed.add(pkg.id)

    def source(self, pkg):
        self.records.Lookup(pkg.current_ver.file_list[0])
        if(len(self.records.source_pkg) == 0):
            return pkg.name
        else:
            return self.records.source_pkg

    def has_revdeps_without_provides(self, pkg):
        self.verboseprint("Reverse depends:", pkg.get_fullname(True))
        for otherdep in pkg.rev_depends_list:
            if self.installed(otherdep.parent_pkg) and \
                    otherdep.parent_pkg.current_ver.id == otherdep.parent_ver.id and \
                    (otherdep.dep_type_enum == apt_pkg.Dependency.TYPE_DEPENDS or \
                    otherdep.dep_type_enum == apt_pkg.Dependency.TYPE_PREDEPENDS):
                self.verboseprint("Found reverse depend:", otherdep.parent_pkg.get_fullname(True))
                return True
        return False

    def collect_provided_revdeps2(self, pkg):
        for otherdep in pkg.rev_depends_list:
            if self.installed(otherdep.parent_pkg) and \
                    otherdep.parent_pkg.current_ver.id == otherdep.parent_ver.id and \
                    (otherdep.dep_type_enum == apt_pkg.Dependency.TYPE_DEPENDS or \
                    otherdep.dep_type_enum == apt_pkg.Dependency.TYPE_PREDEPENDS):
                self.verboseprint("\t", otherdep.parent_pkg.get_fullname(True))
                self.provided_revdeps.append(otherdep.parent_pkg)


    def collect_provided_revdeps(self, pkg):
        if self.installed(pkg):
            for provided in pkg.current_ver.provides_list:
                try:
                    provides_pkg = self.cache[provided[0]]
                    if not self.installed(provides_pkg):
                        self.verboseprint("Found provide:", provides_pkg.get_fullname(True))
                        self.collect_provided_revdeps2(provides_pkg)
                except KeyError as e:
                    self.verboseprint("Package not found:", str(e).strip('"'))

    def collect_revrecommends(self, pkg):
        global type_recommends

        self.verboseprint("Revrecommends:", pkg.get_fullname(True))
        for otherdep in pkg.rev_depends_list:
            if self.installed(otherdep.parent_pkg) and \
                    otherdep.parent_pkg.current_ver.id == otherdep.parent_ver.id and \
                    otherdep.dep_type_enum == type_recommends:
                self.verboseprint("\t", otherdep.parent_pkg.get_fullname(True))
                self.revrecommends.append(otherdep.parent_pkg)

    def has_revdepends_loop(self, pkg):

        for otherdep in pkg.rev_depends_list:
            if self.installed(otherdep.parent_pkg) and \
                    otherdep.parent_pkg.current_ver.id == otherdep.parent_ver.id and \
                    (otherdep.dep_type_enum == apt_pkg.Dependency.TYPE_DEPENDS or \
                    otherdep.dep_type_enum == apt_pkg.Dependency.TYPE_PREDEPENDS) and \
                    not otherdep.parent_pkg.id in self.deps:
                return True
        if self.installed(pkg):
            for provided in pkg.current_ver.provides_list:
                try:
                    provides_pkg = self.cache[provided[0]]
                    if not self.installed(provides_pkg):
                        if self.has_revdepends_loop(provides_pkg):
                            return True
                except KeyError as e:
                    self.verboseprint("Package not found:", str(e).strip('"'))

        return False

    def dependency_version(self, pkg):
        if pkg.id in self.deps and self.deps[pkg.id]:
            return
        self.deps[pkg.id] = True

        for or_group in pkg.current_ver.depends_list.get("PreDepends", []) + \
                pkg.current_ver.depends_list.get("Depends", []):
            for otherdep in or_group:
                if self.installed(otherdep.target_pkg):
                    if not self.has_revdepends_loop(otherdep.target_pkg):
                        self.dependency_version(otherdep.target_pkg)
                    else:
                        self.deps[otherdep.target_pkg.id] = False
                self.dependency_provides(otherdep.target_pkg)

    def dependency_provides(self, pkg):
        if pkg.has_provides:
            for provider in pkg.provides_list:
                if self.installed(provider[2].parent_pkg) and\
                        provider[2].parent_pkg.current_ver.id == provider[2].id:
                    self.dependency_version(provider[2].parent_pkg)

    def dependencies(self, pkg):
        if self.installed(pkg):
            self.dependency_version(pkg)
        self.dependency_provides(pkg)

    def is_peak(self, pkg):
        if not self.installed(pkg):
            return False
        if pkg.essential or pkg.important:
            self.verboseprint("Package is important:", pkg.get_fullname(True))
            return False
        if not (pkg.current_ver.priority == apt_pkg.PRI_OPTIONAL or\
                 pkg.current_ver.priority == apt_pkg.PRI_EXTRA):
            self.verboseprint("Package is not optional:", pkg.get_fullname(True))
            return False

        if self.has_revdeps_without_provides(pkg):
            return False
        self.provided_revdeps = list()
        self.collect_provided_revdeps(pkg)
        self.revrecommends = list()
        self.collect_revrecommends(pkg)

        if len(self.provided_revdeps) == 0 and len(self.revrecommends) == 0:
            return True

        self.deps = dict()
        self.dependencies(pkg)
        pkg_source = self.source(pkg)

        for prov_revd_pkg in self.provided_revdeps:
            if not prov_revd_pkg.id in self.deps:
                self.verboseprint("Found provided reverse depend:", prov_revd_pkg.get_fullname(True))
                return False

        for revr_pkg in self.revrecommends:
            if not revr_pkg.id in self.deps:
                self.verboseprint("Found reverse recommend:", revr_pkg.get_fullname(True))
                return False
            if pkg_source == self.source(revr_pkg) and\
                    not self.deps[revr_pkg.id]:
                return False

        return True
