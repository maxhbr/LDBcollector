import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Callable, Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymongo
import tqdm
from joblib import Parallel, delayed
from packaging.version import InvalidVersion
from packaging.version import parse as parse_v
from pymongo import MongoClient

from .utils import chunks

MONGO_URL = "mongodb://localhost:27017/"
LICENSE_TERMS: pd.DataFrame = pd.read_csv("./app/knowledgebase/licenses_terms_63.csv")
LICENSE_COMPAT: pd.DataFrame = pd.read_csv(
    "./app/knowledgebase/compatibility_63.csv", index_col=0
)
ALL_LICENSES: list = LICENSE_TERMS["license"].tolist()


def get_license_type(license: str) -> str:
    df = LICENSE_TERMS
    this_term = df[df["license"] == license].to_dict(orient="records")
    if this_term:
        this_term = this_term[0]
        copyleft = this_term["copyleft"]
        if copyleft == 0:
            return "Permissive"
        elif copyleft == 1 or copyleft == 2:
            return "Weak Copyleft"
        else:
            return "Strong Copyleft"
    else:
        return "Unknown"


def is_compatible(license_upstream: str, license_downstream: str) -> str:
    df = LICENSE_COMPAT
    if license_upstream in ALL_LICENSES and license_downstream in ALL_LICENSES:
        compatibility_result = str(df.loc[license_upstream, license_downstream])
        if compatibility_result == "0":
            return "Incompatible"
        else:
            return "Compatible"
    return "Unknown"


def get_license_incompatibility(
    client: MongoClient, pkg: str, ver: str, which_tree: str
) -> Tuple[str, List[dict]]:
    pkg_db = client["license"]["package"]
    pkg_doc = pkg_db.find_one({"name": pkg.lower(), "version": ver})
    assert which_tree in ["tree_created", "tree_latest"]

    overall_comp, incompatibilies = "Compatible", []

    if which_tree not in pkg_doc or pkg_doc[which_tree] == []:
        return overall_comp, incompatibilies

    for dep in pkg_doc[which_tree]:
        dep_doc = pkg_db.find_one({"name": dep["name"], "version": dep["version"]})

        if dep_doc:
            comp = is_compatible(dep_doc["license_clean"], pkg_doc["license_clean"])
        else:
            comp = "Unknown"

        if comp == "Incompatible":
            overall_comp = "Incompatible"
            incompatibilies.append(
                {
                    "package": pkg,
                    "version": ver,
                    "date": pkg_doc["release_date"],
                    "license": pkg_doc["license_clean"],
                    "which_tree": which_tree,
                    "dep_name": dep["name"],
                    "dep_version": dep["version"],
                    "dep_license": dep_doc["license_clean"],
                    "is_direct": any(c["from"] == "" for c in dep["constraints"]),
                }
            )
        elif comp == "Unknown" and overall_comp == "Compatible":
            overall_comp = "Unknown"

    return overall_comp, incompatibilies


def get_incompatibility_report(
    client: MongoClient, pkg: str, ver: str, which_tree: str
) -> str:
    pkg_db = client["license"]["package"]
    pkg_doc = pkg_db.find_one({"name": pkg.lower(), "version": ver})
    assert which_tree in ["tree_created", "tree_latest"]

    overall_comp, incomps = get_license_incompatibility(client, pkg, ver, which_tree)

    if overall_comp != "Incompatible":
        return overall_comp

    report = (
        f"{pkg} {ver} ({pkg_doc['license_clean']}) has "
        + f"{len(incomps)} incompatibilities in [{which_tree}]:\n"
    )

    # Builds dep graph
    name2dep = {"": {"name": pkg, "version": "", "constraints": []}}
    from2dep = defaultdict(list)
    for dep in pkg_doc[which_tree]:
        name2dep[dep["name"]] = dep
        for c in dep["constraints"]:
            from2dep[c["from"]].append(dep["name"])

    # Converts to tree using breadth-first search
    tree = {"name": "", "children": []}
    queue = [(tree, dep) for dep in from2dep[""]]
    visited = set()
    while len(queue) > 0:
        node, dep = queue.pop(0)
        node["children"].append({"name": dep, "children": []})
        visited.add(dep)
        for child in from2dep[dep]:
            if not child in visited:
                queue.append((node["children"][-1], child))

    # Print tree with incompatibilities using depth-first search
    incomp2license = {i["dep_name"]: i["dep_license"] for i in incomps}

    def print_tree(node: dict, depth: int = 0) -> str:
        dep = name2dep[node["name"]]
        report = "  " * depth
        report += f"{dep['name']} {dep['version']}"
        if dep["name"] in incomp2license:
            report += f" (INCOMPATIBLE! HAS {incomp2license[dep['name']]})"
        for c in dep["constraints"]:
            source = c["from"] if c["from"] != "" else pkg
            report += f" [{source} ({c['specifier']})]"
        report += "\n"
        for child in node["children"]:
            report += print_tree(child, depth + 1)
        return report

    report += print_tree(tree)

    return report


def get_license_data_single_process(
    packages: list, has_dep_tree: bool = False
) -> Tuple[List[dict], List[dict]]:
    client = MongoClient(MONGO_URL, tz_aware=True)
    package_db = client["license"]["package"]
    samples, incompats = [], []

    for year in range(2006, 2023):
        for package in packages:
            query = {
                "name": package.lower(),
                "release_date": {
                    "$gte": datetime(year, 1, 1, tzinfo=timezone.utc),
                    "$lt": datetime(year, 12, 31, tzinfo=timezone.utc),
                },
                "license_clean": {"$exists": True},
            }
            if has_dep_tree:
                query["tree_created"] = {"$exists": True, "$ne": []}
                query["tree_latest"] = {"$exists": True, "$ne": []}

            if package_db.count_documents(query) == 0:
                continue

            sample = (
                package_db.find(query)
                .sort("release_date", pymongo.DESCENDING)
                .limit(1)
                .next()
            )

            for which_tree in ["tree_created", "tree_latest"]:
                if which_tree not in sample:
                    continue

                overall_comp, incompat = get_license_incompatibility(
                    client, package, sample["version"], which_tree
                )

                samples.append(
                    {
                        "package": package,
                        "version": sample["version"],
                        "date": sample["release_date"],
                        "license": sample["license_clean"],
                        "license_type": get_license_type(sample["license_clean"]),
                        "which_tree": which_tree,
                        "n_deps": len(sample[which_tree]),
                        "compat": overall_comp,
                    }
                )

                incompats.extend(incompat)

    client.close()
    return samples, incompats


def get_license_data(
    has_dep_tree: bool = False, sample: bool = True, n_jobs: int = 1
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    client = MongoClient(MONGO_URL, tz_aware=True)
    package_db = client["license"]["package"]

    if sample:
        with open("dep_resolve/top-pypi-packages-30-days.min.json") as f:
            packages = [r["project"] for r in json.load(f)["rows"]]
    else:
        packages = package_db.distinct("name")

    samples, incompats = [], []

    # samples, incompats = get_samples_single_process(packages, has_dep_tree)
    chunk_lst = chunks(packages, 5)
    res = Parallel(n_jobs=n_jobs, backend="multiprocessing")(
        delayed(get_license_data_single_process)(task, has_dep_tree)
        for task in tqdm.tqdm(chunk_lst, total=len(packages) / 5)
    )
    for sample, incomp in res:
        samples.extend(sample)
        incompats.extend(incomp)

    samples = pd.DataFrame(samples).sort_values(["package", "version"])
    incompats = pd.DataFrame(incompats).sort_values(["package", "version"])
    return samples, pd.DataFrame(incompats)


def get_license_changes_single_process(packages):
    client = MongoClient("mongodb://localhost:27017/", tz_aware=True)
    package_db = client["license"]["package"]
    data = []
    for package in packages:
        package_docs = list(
            package_db.find(
                {"name": package.lower(), "license_clean": {"$exists": True}}
            ).sort("release_date", pymongo.ASCENDING)
        )
        try:
            package_docs = sorted(package_docs, key=lambda x: parse_v(x["version"]))
        except InvalidVersion:
            pass

        if len(package_docs) == 0:
            continue

        licenses = []
        for doc in package_docs:
            # The data is noisy, keep only the clean ones
            if doc["license_clean"] in ["Other", "Unrecognizable"]:
                continue

            if len(licenses) == 0 or licenses[-1] != doc["license_clean"]:
                licenses.append(doc["license_clean"])

                data.append(
                    {
                        "package": package,
                        "version": doc["version"],
                        "date": doc["release_date"],
                        "license": licenses[-1],
                        "license_type": get_license_type(licenses[-1]),
                    }
                )
    return data


def get_license_changes(sample=True) -> pd.DataFrame:
    client = MongoClient("mongodb://localhost:27017/", tz_aware=True)
    package_db = client["license"]["package"]
    if sample:
        with open("dep_resolve/top-pypi-packages-30-days.min.json") as f:
            packages = [r["project"] for r in json.load(f)["rows"]]
    else:
        packages = package_db.distinct("name")
    chunk_lst = chunks(packages, 5)
    res = Parallel(n_jobs=50, backend="multiprocessing")(
        delayed(get_license_changes_single_process)(task)
        for task in tqdm.tqdm(chunk_lst, total=len(packages) / 5)
    )
    data = []
    for i in res:
        data.extend(i)

    return pd.DataFrame(data)


if __name__ == "__main__":
    sample_license_data, _ = get_license_data(sample=True, n_jobs=20)
    sample_license_data.to_csv("data/license_data.csv", index=False)
    all_license_data, _ = get_license_data(sample=False, n_jobs=50)
    all_license_data.to_csv("data/license_data_pypi.csv", index=False)

    sample_license_change_data = get_license_changes()
    sample_license_change_data.to_csv("data/license_changes.csv", index=False)
    all_license_change_data = get_license_changes(sample=False)
    all_license_change_data.to_csv("data/license_changes_pypi.csv", index=False)