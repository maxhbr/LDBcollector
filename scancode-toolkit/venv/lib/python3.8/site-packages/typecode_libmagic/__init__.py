#
# Copyright (c) nexB Inc. and others.
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# 
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
# 
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from os.path import abspath
from os.path import dirname
from os.path import join

from plugincode.location_provider import LocationProviderPlugin


class LibmagicPaths(LocationProviderPlugin):
    def get_locations(self):
        curr_dir = dirname(abspath(__file__))
        data_dir = join(curr_dir, 'data')
        lib_dir = join(curr_dir, 'lib')
        locations = {
            # typecode.libmagic.libdir is not used anymore and deprecated
            # but we are keeping it around for now for backward compatibility
            'typecode.libmagic.libdir': lib_dir,
            'typecode.libmagic.dll': join(lib_dir, 'libmagic.so'),
            'typecode.libmagic.db': join(data_dir, 'magic.mgc'),
        }
        return locations
