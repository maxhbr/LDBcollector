#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/plugincode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.

from plugincode import CodebasePlugin
from plugincode import PluginManager
from plugincode import HookimplMarker
from plugincode import HookspecMarker


stage = "pre_scan"
entrypoint = "scancode_pre_scan"

pre_scan_spec = HookspecMarker(stage)
pre_scan_impl = HookimplMarker(stage)


@pre_scan_spec
class PreScanPlugin(CodebasePlugin):
    """
    A pre-scan plugin base class that all pre-scan plugins must extend.
    """

    pass


pre_scan_plugins = PluginManager(
    stage=stage, module_qname=__name__, entrypoint=entrypoint, plugin_base_class=PreScanPlugin
)
