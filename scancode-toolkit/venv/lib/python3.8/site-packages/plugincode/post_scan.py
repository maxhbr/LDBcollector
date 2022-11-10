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

stage = "post_scan"
entrypoint = "scancode_post_scan"

post_scan_spec = HookspecMarker(project_name=stage)
post_scan_impl = HookimplMarker(project_name=stage)


@post_scan_spec
class PostScanPlugin(CodebasePlugin):
    """
    A post-scan plugin base class that all post-scan plugins must extend.
    """

    pass


post_scan_plugins = PluginManager(
    stage=stage, module_qname=__name__, entrypoint=entrypoint, plugin_base_class=PostScanPlugin
)
