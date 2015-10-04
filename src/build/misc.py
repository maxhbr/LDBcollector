# Copyright 2012  Kuno Woudt

# All software related to the License Database project is licensed under
# the Apache License, Version 2.0. See the file Apache-2.0.txt for more
# information.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

'''
activate licensedb virtual environment
'''
import os
import sys
from os.path import isfile, join

def activate_virtualenv (appname):
    """ This will look for an application specific virtualenv in
    $XDG_DATA_HOME/<appname>/virtualenv and activate it if present. """

    data_home = os.getenv ('XDG_DATA_HOME')
    if not data_home:
        home = os.getenv ('HOME')
        if not home:
            # probably building under docker
            print ('WARNING: $HOME environment variable not set, using /root')
            home = '/root'

        data_home = join (home, '.local', 'share')

    ve_activate = join (data_home, appname, 'virtualenv', 'bin', 'activate_this.py')

    if isfile (ve_activate):
        execfile (ve_activate, dict (__file__ = ve_activate))

