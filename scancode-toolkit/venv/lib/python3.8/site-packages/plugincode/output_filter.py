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

stage = "output_filter"
entrypoint = "scancode_output_filter"

output_filter_spec = HookspecMarker(project_name=stage)
output_filter_impl = HookimplMarker(project_name=stage)


@output_filter_spec
class OutputFilterPlugin(CodebasePlugin):
    """
    Base plugin class for Resource output filter plugins that all output filter
    plugins must extend.

    Filter plugins MUST NOT modify the codebase beyond setting the
    Resource.is_filtered flag on resources.
    """

    pass


output_filter_plugins = PluginManager(
    stage=stage, module_qname=__name__, entrypoint=entrypoint, plugin_base_class=OutputFilterPlugin
)
