# -*- coding: utf-8 -*-

# SPDX-License-Identifier: MIT
# Copyright (c)  Jannis Gebauer and others
# Originally from https://github.com/pyupio/dparse/
# Now maintained at https://github.com/nexB/dparse2

import json
from collections import OrderedDict
from configparser import ConfigParser
from configparser import NoOptionError
from io import StringIO

import toml
import yaml

from packaging.requirements import InvalidRequirement
from packaging.requirements import Requirement as PackagingRequirement
from packaging.specifiers import SpecifierSet

from dparse2.dependencies import Dependency, DependencyFile


# this is a backport from setuptools 26.1
def setuptools_parse_requirements_backport(strs):  # pragma: no cover
    # Copyright (C) 2016 Jason R Coombs <jaraco@jaraco.com>
    #
    # Permission is hereby granted, free of charge, to any person obtaining a
    # copy of this software and associated documentation files (the "Software"),
    # to deal in the Software without restriction, including without limitation
    # the rights to use, copy, modify, merge, publish, distribute, sublicense,
    # and/or sell copies of the Software, and to permit persons to whom the
    # Software is furnished to do so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in
    # all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
    # THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    # FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    # DEALINGS IN THE SOFTWARE.

    """
    Yield ``Requirement`` objects for each specification in `strs`
    `strs` must be a string, or a (possibly-nested) iterable thereof.
    """

    # create a steppable iterator, so we can handle \-continuations
    def yield_lines(strs):
        """Yield non-empty/non-comment lines of a string or sequence"""
        if isinstance(strs, str):
            for s in strs.splitlines():
                s = s.strip()
                # skip blank lines/comments
                if s and not s.startswith("#"):
                    yield s
        else:
            for ss in strs:
                for s in yield_lines(ss):
                    yield s

    lines = iter(yield_lines(strs))

    for line in lines:
        # Drop comments -- a hash without a space may be in a URL.
        if " #" in line:
            line = line[: line.find(" #")]
        # If there is a line continuation, drop it, and append the next line.
        if line.endswith("\\"):
            line = line[:-2].strip()
            line += next(lines)
        yield PackagingRequirement(line)


def parse_requirement_line(line):
    try:
        # setuptools requires a space before the comment. If this isn't the
        # case, add it.
        if "\t#" in line:
            (parsed,) = setuptools_parse_requirements_backport(
                line.replace("\t#", "\t #")
            )
        else:
            (parsed,) = setuptools_parse_requirements_backport(line)

    except InvalidRequirement:
        return

    dep = Dependency(
        name=parsed.name,
        specs=parsed.specifier,
        line=line,
        extras=parsed.extras,
        dependency_type="requirements.txt",
    )
    return dep


class Parser(object):

    def __init__(self, obj):
        self.obj = obj
        self._lines = None

    @property
    def lines(self):
        if self._lines is None:
            self._lines = self.obj.content.splitlines()
        return self._lines


class ToxINIParser(Parser):

    def parse(self):
        parser = ConfigParser()
        parser.read_file(StringIO(self.obj.content))
        for section in parser.sections():
            try:
                content = parser.get(section=section, option="deps")
                for line in content.splitlines():
                    if not line:
                        continue
                    req = parse_requirement_line(line)
                    if req:
                        req.dependency_type = self.obj.file_name
                        self.obj.dependencies.append(req)

            except NoOptionError:
                pass


class CondaYMLParser(Parser):

    def parse(self):
        try:
            data = yaml.safe_load(self.obj.content) or {}
            dependencies = data.get("dependencies") or []
            for dep in dependencies:
                if not isinstance(dep, dict):
                    continue
                lines = dep.get("pip") or []
                for line in lines:
                    req = parse_requirement_line(line)
                    if req:
                        req.dependency_type = self.obj.file_name
                        self.obj.dependencies.append(req)
        except yaml.YAMLError:
            pass


class PipfileParser(Parser):

    def parse(self):
        """
        Parse a Pipfile (as seen in pipenv)
        """
        try:
            data = toml.loads(self.obj.content, _dict=OrderedDict)
            if not data:
                return
            for package_type in ["packages", "dev-packages"]:
                if package_type not in data:
                    continue

                for name, specs in data[package_type].items():
                    # skip on VCS dependencies
                    if not isinstance(specs, str):
                        continue
                    if specs == "*":
                        specs = ""

                    self.obj.dependencies.append(
                        Dependency(
                            name=name,
                            specs=SpecifierSet(specs),
                            dependency_type="Pipfile",
                            line="".join([name, specs]),
                            section=package_type,
                        )
                    )
        except (toml.TomlDecodeError, IndexError):
            pass


class PipfileLockParser(Parser):

    def parse(self):
        """
        Parse a Pipfile.lock (as seen in pipenv)
        """
        try:
            data = json.loads(self.obj.content, object_pairs_hook=OrderedDict)
            if not data:
                return
            for package_type in ["default", "develop"]:
                if not package_type in data:
                    continue
                for name, meta in data[package_type].items():
                    # skip VCS dependencies
                    if "version" not in meta:
                        continue
                    specs = meta["version"]
                    hashes = meta["hashes"]
                    self.obj.dependencies.append(
                        Dependency(
                            name=name,
                            specs=SpecifierSet(specs),
                            dependency_type="Pipfile.lock",
                            hashes=hashes,
                            line="".join([name, specs]),
                            section=package_type,
                        )
                    )
        except ValueError:
            pass


class SetupCfgParser(Parser):

    def parse(self):
        parser = ConfigParser()
        parser.read_file(StringIO(self.obj.content))
        for section in parser.values():
            if section.name == "options":
                options = "install_requires", "setup_requires", "test_require"
                for name in options:
                    content = section.get(name)
                    if not content:
                        continue
                    self._parse_content(content)
            elif section.name == "options.extras_require":
                for content in section.values():
                    self._parse_content(content)

    def _parse_content(self, content):
        for line in content.splitlines():
            if not line:
                continue
            req = parse_requirement_line(line)
            if req:
                req.dependency_type = self.obj.file_name
                self.obj.dependencies.append(req)


def parse(content, file_name=None, path=None, parser=None):
    dep_file = DependencyFile(
        content=content,
        path=path,
        file_name=file_name,
        parser=parser,
    )

    return dep_file.parse()
