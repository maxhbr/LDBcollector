package org.ossreviewtoolkit.tools.curations

import org.gradle.api.DefaultTask
import org.gradle.api.logging.Logging
import org.ossreviewtoolkit.model.Identifier
import org.ossreviewtoolkit.model.PackageCuration
import org.ossreviewtoolkit.model.PackageCurationData
import org.ossreviewtoolkit.model.VcsInfoCurationData
import org.ossreviewtoolkit.model.config.PackageConfiguration
import org.ossreviewtoolkit.utils.common.encodeOr
import org.semver4j.Semver

import java.io.File

private val logger = Logging.getLogger("utils")
private val versionRegex = Regex("^v?\\d+\\.\\d+\\.\\d+\$")

val DefaultTask.curationsDir: File
    get() = project.rootDir.resolve("../../curations")

val DefaultTask.packageConfigurationsDir: File
    get() = project.rootDir.resolve("../../package-configurations")

fun Identifier.toCurationPath() =
    "${type.encodeOr("_")}/${namespace.encodeOr("_")}/${name.encodeOr("_")}.yml"

fun List<PathCurationData>.toPathCurations(): List<PackageCuration> {
    var lastPath = ""

    // Group subsequent versions which belong to the same path.
    val grouped = sortedBy { Semver.coerce(it.tag.removePrefix("v")) }
        .fold(mutableListOf<MutableList<PathCurationData>>()) { acc, cur ->
            if (cur.path != lastPath) {
                acc.add(mutableListOf())
            }
            lastPath = cur.path
            acc.apply { last() += cur }
        }

    return grouped.mapIndexed { index, curations ->
        val firstVersion = curations.first().tag.removePrefix("v")
        val lastVersion = curations.last().tag.removePrefix("v")

        val versionRange = when {
            index == grouped.size - 1 -> "[$firstVersion,)"
            firstVersion == lastVersion -> firstVersion
            else -> "[$firstVersion,$lastVersion]"
        }

        val id = curations.first().id.copy(version = versionRange)
        val path = curations.first().path

        logger.quiet("Creating path curation for id=${id.toCoordinates()} path=$path.")

        PackageCuration(
            id = id.copy(version = versionRange),
            data = PackageCurationData(
                comment = "Set the VCS path of the module inside the multi-module repository.",
                vcs = VcsInfoCurationData(
                    path = path
                )
            )
        )
    }
}

fun PackageConfiguration.expectedPath() =
    "${id.type.encodeOr("_")}/${id.namespace.encodeOr("_")}/${id.name.encodeOr("_")}/" +
            "${id.version.encodeOr("_")}/${if (vcs != null) "vcs" else "source-artifact"}.yml"

fun String.isVersion() = matches(versionRegex)
