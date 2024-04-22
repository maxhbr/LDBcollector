package org.ossreviewtoolkit.tools.curations

import org.ossreviewtoolkit.model.Identifier

data class PathCurationData(
    val id: Identifier,
    val path: String,
    val tag: String
)
