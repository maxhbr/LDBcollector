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
            print ('ERROR: $HOME environment variable not set')
            sys.exit (1)

        data_home = join (home, '.local', 'share')

    ve_activate = join (data_home, appname, 'virtualenv', 'bin', 'activate_this.py')

    if isfile (ve_activate):
        execfile (ve_activate, dict (__file__ = ve_activate))


'''
License class.
This module is used by other python scripts during build stage.
'''

class License (object):
    '''
    Defines and holds a license data.
    '''
    id = None
    uri = None
    replacedBy = None
    earlierVersion = None
    laterVersion = None
    hasVersion = None
    jurisdiction = None
    dcidentifier = None
    plaintext = None

    def __init__ (self, identifier = None):
        self.id = identifier

    def short_name (self):
        """ Return a short display name, e.g. "Apache-1". """

        # This is a quick hack to get a string identical to the value
        # of dc:identifier set by the license_name macro here:
        # http://code.creativecommons.org/viewgit/cc.engine.git/tree/cc/engine/templates/licenses/standard_deed.html#n19

        id = ""
        ver = ""
        jur = ""

        if not self.dcidentifier:
            print ("WARNING:", self.id, "does not have a dc:identifier")
            return None

        if "mark" == self.dcidentifier:
            return "Public Domain"

        if ("devnations" in self.dcidentifier
            or "sampling" in self.dcidentifier):
            id = (self.dcidentifier
                  .replace ("nc", "NC")
                  .replace ("devnations", "Devnations")
                  .replace ("sampling", "Sampling"))
        else:
            id = self.dcidentifier.upper ()

        if self.hasVersion:
            ver = " " + self.hasVersion

        if self.jurisdiction:
            j = self.jurisdiction.replace ("http://creativecommons.org/international/", "")
            jur = " " + j.split ("/")[0].upper ()

        return "CC %s%s%s" % (id, ver, jur)


    def __str__ (self):
        return (", ".join (filter (lambda x: x, [
                        self.id, self.uri, self.replacedBy,
                        self.earlierVersion, self.laterVersion])))


def __init__ ():
    """ init module """
