import z3
import logging

from pprint import pformat
from collections import OrderedDict
from typing import List, Set, Dict, Tuple, Optional
from datetime import datetime
from datetime import timezone
from pymongo import MongoClient
from packaging.requirements import Requirement, InvalidRequirement
from packaging.version import parse as parse_version, InvalidVersion


logger = logging.getLogger(__name__)


class PackageCache:
    def __init__(self, mongo_uri: str,root_package: str, root_version: str):
        self.mongo_client = MongoClient(mongo_uri, tz_aware=True)
        self.pkgdb = self.mongo_client["license"]["package"]
        self.pkg2vers: Dict[str, List[str]] = dict()
        self.root_package = root_package
        self.root_version = root_version
    def get_index(self, package: str, version: str) -> int:
        if package == self.root_package and version == self.root_version:
            return 0
        if package not in self.pkg2vers:
            versions = [x["version"] for x in self.pkgdb.find({"name": package})]
            try:
                self.pkg2vers[package] = sorted(versions, key=parse_version)
            except InvalidVersion:
                self.pkg2vers[package] = sorted(versions)
        return self.pkg2vers[package].index(version) - len(self.pkg2vers[package])

    def get_version(self, package: str, index: int) -> str:
        return self.pkg2vers[package][index]

    def __del__(self):
        self.mongo_client.close()


class Z3DependencyResolver:
    def __init__(self, mongo_uri: str, package: str, version : str = "0.0.1"):
        self.package = package
        self.version = version
        self.mongo_uri = mongo_uri
        self.mongo_client = MongoClient(mongo_uri, tz_aware=True)
        self.pkg_cache = PackageCache(mongo_uri,self.package,self.version)

    def match_version(
        self,
        req: Requirement,
        before: datetime,
    ) -> List[Tuple[str, List[str]]]:
        package_db = self.mongo_client["license"]["package"]
        candidates = []
        #max_version = "0.0.0"
        for metadata in package_db.find({"name": req.name.lower()}):
            if metadata["release_date"] > before:
                continue
            # if metadata["version"] > max_version:
            #         max_version = metadata["version"]
            try:
                if not req.specifier or metadata["version"] in req.specifier:
                    candidates.append((metadata["version"], metadata["requires_dist"]))
            except InvalidVersion:
                continue
        # if not candidates:
        #     if len(req.specifier) == 1 and next(iter(req.specifier)).operator == "==":
        #         version = next(iter(req.specifier)).version
        #         if version > max_version:
        #             max_pkg = package_db.find_one({"name": req.name.lower(), "version": max_version})
        #             if max_pkg:
        #                 candidates.append((max_version, max_pkg["requires_dist"]))
        return candidates

    def build_solution_space(
        self,
        require_dist: List[str],
        extras: Set[str],
        before: datetime,
    ) -> Tuple[Dict[Tuple[str, str], List[str]], Dict[str, List[int]]]:
        pkgver2reqs = OrderedDict({(self.package, self.version): require_dist})
        req2cands = dict()
        req_queue = [d for d in reversed(require_dist)]
        req_set = set(req_queue)

        while len(req_queue) > 0:
            try:
                req_text = req_queue.pop(0)
                req = Requirement(req_text)
                pkg_name = req.name.lower()
                if req.marker is not None and not req.marker.evaluate():
                    continue
                if req.extras is not None and not req.extras.issubset(extras):
                    continue
            except (InvalidRequirement, InvalidVersion) as ex:
                logger.warning("%s: %s", ex, req_text)
                continue

            candidates = self.match_version(req, before)

            for ver, next_requires in candidates:
                pkgver2reqs[(pkg_name, ver)] = next_requires
                for r in reversed(next_requires):
                    if r not in req_set:
                        req_set.add(r)
                        req_queue.append(r)

            req2cands[req_text] = [
                self.pkg_cache.get_index(pkg_name, ver) for ver, _ in candidates
            ]

        return pkgver2reqs, req2cands

    def build_z3_constraints(
        self,
        pkgver2reqs: Dict[Tuple[str, str], List[str]],
        req2cands: Dict[str, List[int]],
    ) -> Tuple[z3.Optimize, Dict[str, z3.ArithRef], Set[str]]:
        z3solver = z3.Optimize()
        var_dict = OrderedDict({self.package: z3.Int(self.package)})
        root_index = self.pkg_cache.get_index(self.package, self.version)

        z3solver.add(var_dict[self.package] == root_index)

        for pkg, ver in pkgver2reqs:
            if pkg not in var_dict:
                var_dict[pkg] = z3.Int(pkg)
                z3solver.add(var_dict[pkg] <= 0)

        ignored_requires = set()
        for (pkg, ver), reqs in pkgver2reqs.items():
            # Add an imply-clause for each possible version
            for req in reqs:
                # Ignored in the get_solution_space() step
                if req not in req2cands:
                    continue
                # Included, but we cannot find a good version
                if req2cands[req] == []:
                    ignored_requires.add((pkg, ver, req))
                    continue
                next_pkg = Requirement(req).name.lower()
                z3solver.add(
                    z3.Implies(
                        var_dict[pkg] == self.pkg_cache.get_index(pkg, ver),
                        z3.Or([var_dict[next_pkg] == i for i in req2cands[req]]),
                    )
                )

        return z3solver, var_dict, ignored_requires

    def get_solution(
        self, z3solver: z3.Optimize, var_dict: Dict[str, z3.ArithRef]
    ) -> Optional[Dict[str, str]]:
        for var in var_dict:
            z3solver.maximize(var_dict[var])
        z3solver.maximize(z3.Sum([var_dict[var] for var in var_dict]))

        if z3solver.check() == z3.sat:
            logger.debug(z3solver.model())
            dep = {}
            for p in z3solver.model():
                if z3solver.model()[p].as_long() < 0:
                    index = z3solver.model()[p].as_long()
                    dep[p.name()] = self.pkg_cache.get_version(p.name(), index)
            return dep
        else:
            logger.debug("unsat")
            return None

    def resolve(
        self,
        require_dist: List[str],
        extras: Set[str] = None,
        before: datetime = datetime.now(tz=timezone.utc),
    ) -> Optional[Dict[str, str]]:
        extras = set() if extras is None else extras
        pfmt_args = {"compact": True, "width": 200}

        logger.debug(
            "Resolving %s-%s, requires = %s, extras = %s, before = %s",
            self.package,
            self.version,
            require_dist,
            extras,
            before,
        )

        pkgver2reqs, req2cands = self.build_solution_space(require_dist, extras, before)
        logger.debug("(pkg, ver) -> reqs: \n%s", pformat(pkgver2reqs, **pfmt_args))
        logger.debug("req -> cand vers: \n%s", pformat(req2cands, **pfmt_args))

        z3solver, var_dict, ignored = self.build_z3_constraints(pkgver2reqs, req2cands)
        logger.debug("Assertions: \n%s", "\n".join(map(str, z3solver.assertions())))
        logger.debug("Ignored constraints: %s", pformat(ignored, **pfmt_args))

        return self.get_solution(z3solver, var_dict)

    def __del__(self):
        self.mongo_client.close()


if __name__ == "__main__":


    logging.basicConfig(
        format="%(asctime)s (Process %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.DEBUG,
    )

    test_data = [
        ("mlehub", "0.0"),
        ("openapi-schema-validator", "0.1.1"),
        ("amundsen-databuilder", "7.4.2"),
    ]
    mongo_uri = "mongodb://localhost:27017/"

    for name, version in test_data:
        client = MongoClient(mongo_uri, tz_aware=True)
        package_db = client["license"]["package"]
        sample = package_db.find_one({"name": name, "version": version})

        dr = Z3DependencyResolver(mongo_uri, name, version)
        dep_tree = dr.resolve(sample["requires_dist"], before=sample["release_date"])
        logger.info("Resolved: %s", dep_tree)

        for item in sample["tree_created"]:
            dep, ver = item["name"].lower(), item["version"]
            if dep not in dep_tree or dep_tree[dep] != ver:
                logger.warning("Resolution mismatch for %s", dep)

    logger.info("Done!")
    exit()
