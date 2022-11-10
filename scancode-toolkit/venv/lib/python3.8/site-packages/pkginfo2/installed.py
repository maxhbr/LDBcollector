import glob
import io
import os
import sys
import warnings

from .distribution import Distribution


class Installed(Distribution):

    def __init__(self, package, metadata_version=None):
        self.package = package
        _, self.package_name = os.path.split(package)
        self.metadata_version = metadata_version
        self.extractMetadata()

    def read(self):
        if not (self.package and os.path.isdir(self.package)):
            return
        opj = os.path.join

        for candidate in os.listdir(self.package):
            if not candidate.endswith(('.dist-info', '.egg-info', 'EGG-INFO',)):
                continue
            candidate = opj(self.package, candidate)

            for metafile in ('METADATA', 'PKG-INFO'):
                content = get_content(candidate, metafile=metafile,)
                if content is not None:
                    return content


def get_content(candidate, metafile):
    if os.path.isdir(candidate):
        path = os.path.join(candidate, metafile)
    elif os.path.isfile(candidate):
        path = candidate
    else:
        return

    with io.open(path, errors='ignore') as f:
        return f.read()
