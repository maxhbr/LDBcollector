# -*- coding: utf-8 -*-

# SPDX-License-Identifier: MIT
# Copyright (c)  Jannis Gebauer and others
# Originally from https://github.com/pyupio/dparse/
# Now maintained at https://github.com/nexB/dparse2

import json


class UnknownDependencyFileError(Exception):
    pass


class Dependency:

    def __init__(
        self,
        name,
        specs,
        line,
        source="pypi",
        meta={},
        extras=[],
        hashes=(),
        dependency_type=None,
        section=None,
    ):
        self.name = name
        self.key = name.lower().replace("_", "-")
        self.specs = specs
        self.line = line
        self.source = source
        self.meta = meta
        self.hashes = hashes
        self.dependency_type = dependency_type
        self.extras = extras
        self.section = section

    def __str__(self):  # pragma: no cover
        return "Dependency({name}, {specs}, {line})".format(
            name=self.name, specs=self.specs, line=self.line
        )

    def serialize(self):
        return {
            "name": self.name,
            "specs": self.specs,
            "line": self.line,
            "source": self.source,
            "meta": self.meta,
            "hashes": self.hashes,
            "dependency_type": self.dependency_type,
            "extras": self.extras,
            "section": self.section,
        }

    @classmethod
    def deserialize(cls, d):
        return cls(**d)

    @property
    def full_name(self):
        if self.extras:
            return "{}[{}]".format(self.name, ",".join(self.extras))
        return self.name


class DependencyFile:

    def __init__(
        self,
        content,
        path=None,
        file_name=None,
        parser=None,
    ):
        self.content = content
        self.file_name = file_name
        self.path = path

        self.dependencies = []
        self.resolved_files = []
        self.is_valid = False

        if not parser:
            from dparse2 import parser as parser_class

            parsers_by_file_name = {
                "tox.ini": parser_class.ToxINIParser,
                "conda.yml": parser_class.CondaYMLParser,
                "Pipfile": parser_class.PipfileParser,
                "Pipfile.lock": parser_class.PipfileLockParser,
                "setup.cfg": parser_class.SetupCfgParser,
            }

            parser = parsers_by_file_name.get(file_name)

            parsers_by_file_end = {
                ".yml": parser_class.CondaYMLParser,
                ".ini": parser_class.ToxINIParser,
                "Pipfile": parser_class.PipfileParser,
                "Pipfile.lock": parser_class.PipfileLockParser,
                "setup.cfg": parser_class.SetupCfgParser,
            }

            if not parser and path:
                for ends, prsr in parsers_by_file_end.items():
                    if path.endswith(ends):
                        parser = prsr
                        break
        if parser:
            self.parser = parser
        else:
            raise UnknownDependencyFileError

        self.parser = self.parser(self)

    def serialize(self):
        return {
            "content": self.content,
            "path": self.path,
            "dependencies": [dep.serialize() for dep in self.dependencies],
        }

    @classmethod
    def deserialize(cls, d):
        dependencies = [
            Dependency.deserialize(dep) for dep in d.pop("dependencies", [])
        ]
        instance = cls(**d)
        instance.dependencies = dependencies
        return instance

    def json(self):  # pragma: no cover
        return json.dumps(self.serialize(), indent=2)

    def parse(self):
        self.parser.parse()
        self.is_valid = self.dependencies or self.resolved_files
        return self
