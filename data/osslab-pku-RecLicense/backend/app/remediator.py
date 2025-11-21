import os
import z3
import logging
import argparse
import traceback
import pandas as pd
import multiprocessing as mp

from pprint import pformat
from collections import defaultdict, OrderedDict
from typing import List, Set, Dict, Tuple, Optional
from datetime import datetime, timezone
from pymongo import MongoClient
from packaging.requirements import Requirement, InvalidRequirement
from packaging.version import InvalidVersion, parse as parse_version
from .analysis import is_compatible
logging.basicConfig(
    filename=f"./app/logging/logging.log",
    filemode='a',
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# class PackageCache:
#     def __init__(self, mongo_uri: str):
#         self.mongo_client = MongoClient(mongo_uri, tz_aware=True)
#         self.pkgdb = self.mongo_client["license"]["package"]
#         self.pkg2vers: Dict[str, List[str]] = dict()

#     def get_index(self, package: str, version: str) -> int:
#         if package not in self.pkg2vers:
#             versions = [x["version"] for x in self.pkgdb.find({"name": package})]
#             try:
#                 self.pkg2vers[package] = sorted(versions, key=parse_version)
#             except InvalidVersion:
#                 self.pkg2vers[package] = sorted(versions)
#         return self.pkg2vers[package].index(version) - len(self.pkg2vers[package])

#     def get_version(self, package: str, index: int) -> str:
#         return self.pkg2vers[package][index]

#     def __del__(self):
#         self.mongo_client.close()
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

class MigrationKnowledgeBase:
    def __init__(self, mongo_uri: str, path: str = "./app/knowledgebase"):
        migrations = pd.read_csv(os.path.join(path, "migrations.csv"))
        import2pkg = pd.read_csv(os.path.join(path, "p2i.csv"))
        weights = pd.read_csv(os.path.join(path, "migration_weight.csv"))
        import2pkg = {
            im: pkg for pkg, im in zip(import2pkg["package"], import2pkg["import"])
        }

        self.rules = defaultdict(set)
        client = MongoClient(mongo_uri, tz_aware=True)
        package_db = client["license"]["package"]
        for rem_lib, add_lib in set(zip(migrations.rem_lib, migrations.add_lib)):
            if rem_lib not in import2pkg:
                import2pkg[rem_lib] = rem_lib
            if add_lib not in import2pkg:
                import2pkg[add_lib] = add_lib
            rem_lib, add_lib = import2pkg[rem_lib].lower(), import2pkg[add_lib].lower()

            if package_db.find_one({"name": rem_lib}) is None:
                continue
            if package_db.find_one({"name": add_lib}) is None:
                continue

            self.rules[rem_lib].add(add_lib)
            self.rules[add_lib].add(rem_lib)

        self.weights = defaultdict(int)
        for pair, weight in zip(weights.pattern, weights.num):
            p1, p2 = pair.split(" ")
            if (p1, p2) in self.rules:
                self.weights[(p1, p2)] = int(weight)
            if (p2, p1) in self.rules:
                self.weights[(p2, p1)] = int(weight)


class Z3Remediator:
    def __init__(self, mongo_uri: str, package: str, version: str, license: str):
        self.package = package.lower()
        self.version = version
        self.license = license
        self.mongo_uri = mongo_uri
        self.mongo_client = MongoClient(mongo_uri, tz_aware=True)
        self.pkg_cache = PackageCache(mongo_uri, package, version)
        self.mig_base = MigrationKnowledgeBase(mongo_uri)
        for key in self.mig_base.rules:
            s = set()
            for i in self.mig_base.rules[key]:
                s.add(i.lower())
            if len(s) != len(self.mig_base.rules[key]):
                print(key, self.mig_base.rules[key])

    def match_version(
        self,
        req: Requirement,
        before: datetime,
    ) -> Tuple[List[Tuple[str, List[str]]], List[str]]:
        package_db = self.mongo_client["license"]["package"]
        candidates, incompatible_candidates = [], []
        for metadata in package_db.find({"name": req.name.lower()}):
            if metadata["release_date"] > before:
                continue
            try:
                sat_req = not req.specifier or metadata["version"] in req.specifier
                compat = is_compatible(metadata["license_clean"], self.license)
                if sat_req and compat != "Incompatible":
                    candidates.append((metadata["version"], metadata["requires_dist"]))
                if sat_req and compat == "Incompatible":
                    incompatible_candidates.append(metadata["version"])
            except InvalidVersion:
                continue
        return candidates, incompatible_candidates

    def build_solution_space(
        self,
        require_dist: List[str],
        extras: Set[str],
        before: datetime,
    ) -> Tuple[
        Dict[Tuple[str, str], List[str]],
        Dict[str, List[int]],
        Set[str],
        Dict[str, List[str]],
    ]:
        pkgver2reqs = OrderedDict({(self.package, self.version): require_dist})
        req2cands, direct_deps, migrations = dict(), set(), defaultdict(list)
        req_queue = [d for d in reversed(require_dist)]
        req_set = set(req_queue)

        logger.info("Start build Solution Space...")
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

            # Constraint of direct dependency can be violated
            if req_text in require_dist:
                direct_deps.add(pkg_name)
                req = Requirement(pkg_name)

            candidates, incomp_cands = self.match_version(req, before)
            logger.debug("Candidates for %s: %s", req_text, candidates)
            for ver, next_requires in candidates:
                pkgver2reqs[(pkg_name, ver)] = next_requires
                for r in reversed(next_requires):
                    if r not in req_set:
                        req_set.add(r)
                        req_queue.append(r)
           
            # Add possible migrations to the queue for direct deps
            logger.debug("Start addressing direct deps...")
            if pkg_name in direct_deps:
                for alternative_pkg in self.mig_base.rules[req.name.lower()]:
                    r = alternative_pkg.lower()
                    if r not in req_set:
                        req_queue.append(r)
                        req_set.add(r)
                        migrations[pkg_name].append(r)

            req2cands[req_text] = []
            for ver, _ in candidates:
                req2cands[req_text].append(self.pkg_cache.get_index(pkg_name, ver))
            for ver in incomp_cands:  # Positive value constraint as a strict conflict
                req2cands[req_text].append(-self.pkg_cache.get_index(pkg_name, ver))

        return pkgver2reqs, req2cands, direct_deps, migrations

    def build_z3_constraints(
        self,
        pkgver2reqs: Dict[Tuple[str, str], List[str]],
        req2cands: Dict[str, List[int]],
    ) -> Tuple[z3.Optimize, Dict[str, z3.ArithRef], Set[str]]:
        z3solver = z3.Optimize()
        var_dict = OrderedDict({self.package: z3.Int(self.package)})
        root_index = self.pkg_cache.get_index(self.package, self.version)

        z3solver.add(var_dict[self.package] == root_index)

        for req in req2cands:
            pkg = Requirement(req).name.lower()
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
                candidate_vers = [var_dict[next_pkg] == i for i in req2cands[req]]
                # Direct deps could be removed
                if self.package == pkg and self.version == ver:
                    candidate_vers.append(var_dict[next_pkg] == 0)
                z3solver.add(
                    z3.Implies(
                        var_dict[pkg] == self.pkg_cache.get_index(pkg, ver),
                        z3.Or(candidate_vers),
                    )
                )

        return z3solver, var_dict, ignored_requires

    def cost(
        self,
        original_tree: Dict[str, int],
        var_dict: Dict[str, z3.ArithRef],
        migrations: Dict[str, List[str]],
        direct_deps: Set[str],
    ):
        c = 0
        abs = lambda x: z3.If(x >= 0, x, -x)
        for pkg, val in var_dict.items():
            original_val = original_tree.get(pkg, 0)
            if pkg in direct_deps and pkg in migrations:
                cons = []
                for alter in migrations[pkg]:
                    if alter in var_dict and alter != self.package:
                        cons.append(z3.If(var_dict[alter] < 0, 1, 0))
                c = z3.Sum(
                    c,
                    z3.If(z3.And(var_dict[pkg] == 0, z3.Sum(cons) > 0), 10, 0),
                    z3.If(z3.And(var_dict[pkg] == 0, z3.Sum(cons) == 0), 100, 0),
                    z3.If(z3.And(var_dict[pkg] != 0), abs(val - original_val), 0),
                )
            elif pkg in original_tree:
                c = z3.Sum(c, z3.If(var_dict[pkg] != 0, abs(val - original_val), 100))
            else:
                c = z3.Sum(c, z3.If(var_dict[pkg] != 0, 10, 0))
        return c

    def filter_isolated(self, tree: Dict[str, int], pkgver2reqs,req2cands,migrations,direct_deps) -> Dict[str, int]:
        """Remove isolated packages from the tree"""
        que=[]
        s=set()
        new_tree = {}
        for direct_dep in direct_deps:
            if direct_dep in tree:
                new_tree[direct_dep] = tree[direct_dep]
                if direct_dep not in s:
                    s.add(direct_dep)
                    que.append(direct_dep)
        for direct_dep in migrations:
            for alter in migrations[direct_dep]:
                if alter in tree and direct_dep not in tree:
                    new_tree[alter] = tree[alter]
                    if alter not in s:
                        s.add(alter)
                        que.append(alter)
        while(que):
            pkg=que.pop(0)
            try:
                ver=self.pkg_cache.get_version(pkg, tree[pkg])
            except:
                logger.warning(f"Cannot find {pkg} {tree[pkg]} in the package cache")
            if (pkg, ver) in pkgver2reqs:
                for req in pkgver2reqs[(pkg, ver)]:
                    try:
                        req_name=Requirement(req).name.lower()
                    except:
                        continue
                    if (req_name in tree and req in req2cands and tree[req_name] in req2cands[req]):
                        new_tree[req_name] = tree[req_name]
                        if req_name not in s:
                            s.add(req_name)
                            que.append(req_name)
                        
                
        return new_tree
    def remediate(
        self,
        require_dist: List[str],
        original_tree: Dict[str, str],
        extras: Set[str] = None,
        before: datetime = datetime.now(tz=timezone.utc),
    ) -> Optional[Tuple[Dict[str, str], Set[str]]]:
        # get the index of the original tree
        original_tree = {
            package: self.pkg_cache.get_index(package, version)
            for package, version in original_tree.items()
        }

        extras = set() if extras is None else extras
        pfmt_args = {"compact": True, "width": 200}

        pkgver2reqs, req2cands, direct_deps, migrations = self.build_solution_space(
            require_dist, extras, before
        )
        logger.debug("(pkg, ver) -> reqs: \n%s", pformat(pkgver2reqs, **pfmt_args))
        logger.debug("req -> cand vers: \n%s", pformat(req2cands, **pfmt_args))
        logger.debug("direct_dep -> migrations: \n%s", pformat(migrations, **pfmt_args))

        z3solver, var_dict, ignored = self.build_z3_constraints(pkgver2reqs, req2cands)
        logger.debug("Assertions: \n%s", "\n".join(map(str, z3solver.assertions())))

        logger.debug("Ignored constraints: %s", pformat(ignored, **pfmt_args))

        min_cost = z3solver.minimize(
            self.cost(original_tree, var_dict, migrations, direct_deps)
        )
                
        new_trees = []
        original_tree = {
            i: self.pkg_cache.get_version(i, original_tree[i]) for i in original_tree
        }
        for _ in range(5):
            if z3solver.check() == z3.sat:
                logger.debug(z3solver.model())
                new_tree = {}
                for p in z3solver.model():
                    if z3solver.model()[p].as_long() < 0:
                        # new_tree[p.name()] = self.pkg_cache.get_version(
                        #     p.name(), z3solver.model()[p].as_long()
                        # )
                        new_tree[p.name()] = z3solver.model()[p].as_long()
                logger.debug("Cost: %s", min_cost.value())
                
                new_tree = self.filter_isolated(new_tree,pkgver2reqs,req2cands,migrations,direct_deps)
                new_tree = {i:self.pkg_cache.get_version(i,new_tree[i]) for i in new_tree}
                new_trees.append(new_tree)
                cons = []
                for var in z3solver.model():
                    if (
                        new_tree.get(var.name(), 0) != 0
                        and original_tree.get(var.name(), 0) == 0
                        and var.name()
                        in [i for key in migrations for i in migrations[key]]
                    ):  # migration
                        cons.append(0 == var())  # delete it
                    elif (
                        new_tree.get(var.name(), 0) == 0
                        and original_tree.get(var.name(), 0) != 0
                    ):  # delete package
                        continue
                    elif new_tree.get(var.name(), 0) != original_tree.get(
                        var.name(), 0
                    ):  # update package version
                        if var.name() in direct_deps:
                            cons.append(0 == var())  # delete it
                if cons:
                    z3solver.add(z3.Or(cons))
                else:
                    break

            else:
                logger.info("Unsat")
                # return None
                break
        logger.info("New trees have been generated")
        return new_trees, direct_deps

    def summarize_changes(
        self,
        direct_deps: List[str],
        original_tree: Dict[str, str],
        new_tree: Dict[str, str],
    ) -> List[str]:
        changes = []

        for i in new_tree:
            if i in original_tree and new_tree[i] != original_tree[i]:
                changes.append(
                    f"Change {i} version from {original_tree[i]} to {new_tree[i]}"
                )

        for i in original_tree:
            if i not in new_tree and i in direct_deps:
                if i in self.mig_base.rules:
                    for r in self.mig_base.rules[i]:
                        if r in new_tree and r != self.package:
                            changes.append(f"Migrate {i} to {r}")
                            break
                    else:
                        changes.append(f"Remove {i}")
                else:
                    changes.append(f"Remove {i}")

        return changes

    def __del__(self):
        self.mongo_client.close()


def get_remediation(mongo_uri: str, package: str, version: str,requires_dist, dep_tree, license) -> dict:
    remed = {"package": package, "version": version, "changes": [], "new_tree": []}

    client = MongoClient(mongo_uri, tz_aware=True)
    package_db = client["license"]["package"]
    #sample = package_db.find_one({"name": package, "version": version})
    before = datetime.now(tz=timezone.utc)
    #requires_dist, before = sample["requires_dist"], sample["release_date"]
    original_tree = {i.lower(): dep_tree[i] for i in dep_tree}
    logger.info("Original tree: %s", original_tree)
    remed["original_tree"]=original_tree
    dr = Z3Remediator(mongo_uri, package, version, license)
    new_trees, direct_deps = dr.remediate(requires_dist, original_tree, before=before)
    for new_tree in new_trees:
        remed["changes"].append(
            dr.summarize_changes(direct_deps, original_tree, new_tree)
        )
        remed["new_tree"].append(new_tree)

    client.close()
    return remed


def remediation_worker(mongo_uri: str, pkg: str, ver: str) -> dict:
    try:
        logger.info("Remediate for %s %s", pkg, ver)
        return get_remediation(mongo_uri, pkg, ver)
    except Exception as ex:
        logger.error("%s %s: %s\n%s", pkg, ver, ex, traceback.format_exc())
        return {"package": pkg, "version": ver, "error": str(ex)}


def get_remediation_all(mongo_uri: str):
    incompats = pd.read_csv("res/license_incompatibilities.csv")
    incompat_set = set(zip(incompats.package, incompats.version))
    params = [(mongo_uri, pkg, ver) for pkg, ver in incompat_set]
    with mp.Pool(mp.cpu_count() // 2) as pool:
        result = pool.starmap(remediation_worker, params)
    result = pd.DataFrame(result).sort_values(by=["package", "version"])
    result.to_csv("res/remediation.csv", index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scope", choices=["one", "all"])
    parser.add_argument("-n", "--name", type=str, required=False)
    parser.add_argument("-v", "--version", type=str, required=False)
    parser.add_argument(
        "--mongo_uri", type=str, required=False, default="mongodb://localhost:27017/"
    )
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s (Process %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.INFO if args.scope == "all" else logging.DEBUG,
    )

    if args.scope == "one":
        remed = get_remediation(args.mongo_uri, args.name, args.version)
        logger.info("Remediated: %s", remed["new_tree"])
        logger.info("Changes: %s", remed["changes"])
    else:
        get_remediation_all(args.mongo_uri)

    logging.info("Done!")


if __name__ == "__main__":
    main()