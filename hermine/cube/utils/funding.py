# SPDX-FileCopyrightText: 2023 Hermine-team <hermine@inno3.fr>
#
# SPDX-License-Identifier: AGPL-3.0-only

import requests
import json
from packageurl import PackageURL
import time

from django.db import transaction
from license_expression import get_spdx_licensing, BaseSymbol

from cube.models import Funding
from cube.serializers import LicenseSerializer


def guess_type(url):
    if "tidelift" in url:
        type = "tidelift"
    elif "github.com/sponsors" in url:
        type = "github"
    elif "opencollective.com" in url:
        type = "opencollective"
    elif "patreon.com" in url:
        type = "patreon"
    elif "liberapay.com" in url:
        type = "liberapay"
    else:
        type = "custom"
    return type


def get_packagist_funding(namespace, name):
    # namespace = "api-platform"
    # name = "core"
    full_name = f"{namespace}/{name}"
    json_url = f"https://repo.packagist.org/p2/{full_name}.json"
    try:
        r = requests.get(json_url)
        data = r.json()
        # We want uptodate info, so we only check the latest release
        fundings = data["packages"][full_name][0].get("funding")
    except requests.exceptions.RequestException as e:
        print(f"Error while looking up funding: {e}")
        fundings = None
    return fundings


def get_pypi_funding(name):
    json_url = f"https://pypi.org/pypi/{name}/json/"
    try:
        r = requests.get(json_url)
        data = r.json()
        fundings = list()
        project_urls = data["info"].get("project_urls")
        if project_urls:
            for (url_type, url) in project_urls.items():
                if url_type == "Funding" or guess_type(url) != "custom":
                    type = guess_type(url)
                    fundings.append({"type": type, "url": url})
    except requests.exceptions.RequestException as e:
        print(f"Error while looking up funding: {e}")
        fundings = None
    return fundings


def get_npm_funding(namespace, name):
    if namespace:
        fullname = f"{namespace}/{name}"
    else:
        fullname = f"{name}"
    json_url = f"https://registry.npmjs.org/{fullname}/"
    try:
        r = requests.get(json_url)
        data = r.json()
        fundings = list()
        normalized_fundings = list()
        versions = data.get("versions")
        # We take the most up to date info
        if versions:
            for number, version in versions.items():
                version_fundings = version.get("funding")
                if version_fundings:
                    fundings = version_fundings
        # We have to normalise, because fundings can be either a (type, url) dict, a string
        # or a list of those
        if isinstance(fundings, str):
            url = fundings
            normalized_fundings.append({"type": guess_type(url), "url": url})
        elif isinstance(fundings, list):
            for i in range(len(fundings)):
                if isinstance(fundings[i], str):
                    url = fundings[i]
                    normalized_fundings.append({"type": guess_type(url), "url": url})
                elif (
                    isinstance(fundings[i], dict)
                    and "url" in fundings[i]
                    and "type" not in fundings[i]
                ):
                    fundings[i]["type"] = guess_type(fundings[i]["url"])
                    normalized_fundings.append(fundings[i])
                else:
                    normalized_fundings.append(fundings[i])
        elif isinstance(fundings, dict):
            if "url" in fundings and "type" not in fundings:
                fundings["type"] = guess_type(fundings["url"])
            normalized_fundings.append(fundings)
    except requests.exceptions.RequestException as e:
        print(f"Error while looking up funding: {e}")
        normalized_fundings = None
    return normalized_fundings


def get_fundings_from_purl(purl):
    fundings = None
    purl_obj = PackageURL.from_string(purl)
    if purl_obj.type == "composer":
        fundings = get_packagist_funding(purl_obj.namespace, purl_obj.name)
    elif purl_obj.type == "pypi":
        fundings = get_pypi_funding(purl_obj.name)
    elif purl_obj.type == "npm":
        fundings = get_npm_funding(purl_obj.namespace, purl_obj.name)
    return fundings
