package org.ossreviewtoolkit.tools.curations

import com.fasterxml.jackson.module.kotlin.readValue
import org.gradle.api.DefaultTask
import org.gradle.api.GradleException
import org.gradle.api.tasks.TaskAction
import org.ossreviewtoolkit.model.PackageCuration
import org.ossreviewtoolkit.model.mapper
import org.ossreviewtoolkit.utils.spdx.SpdxExpression
import org.semver4j.RangesList
import org.semver4j.RangesListFactory

open class VerifyPackageCurationsTask : DefaultTask() {
    init {
        group = "verification"
    }

    @TaskAction
    fun verify() {
        var fileCount = 0
        var curationCount = 0
        val issues = mutableListOf<String>()

        curationsDir.walk().filter { it.isFile }.forEach { file ->
            fileCount++

            val relativePath = file.relativeTo(curationsDir).invariantSeparatorsPath

            runCatching {
                if (file.extension != "yml") {
                    issues += "The file '$relativePath' does not use the expected extension '.yml'."
                }

                val curations = file.mapper().readValue<List<PackageCuration>>(file)

                curationCount += curations.size

                if (curations.isEmpty()) {
                    issues += "The file '$relativePath' does not contain any curations."
                }

                curations.forEach { curation ->
                    if (curation.id.name.isBlank()) {
                        issues += "Only curations for specific packages are allowed, but the curation for package " +
                                "'${curation.id.toCoordinates()}' in file '$relativePath' does not have a package name."
                    }

                    val version = curation.id.version
                    if (version.isNotBlank() && version.hasVersionRangeIndicators()) {
                        val range = RangesListFactory.create(version)
                        if (range.get().size == 0) {
                            issues += "The version of package '${curation.id.toCoordinates()}' in file " +
                                    "'$relativePath' contains version range indicators, but cannot be parsed to a " +
                                    "valid version range."
                        }
                    }

                    if (curation.data.authors != null) {
                        issues += "Curating authors is not allowed, but the curation for package " +
                                "'${curation.id.toCoordinates()}' in file '$relativePath' sets the authors to " +
                                "'${curation.data.authors}'."
                    }

                    if (curation.data.concludedLicense != null) {
                        issues += "Curating concluded licenses is not allowed, but the curation for package " +
                                "'${curation.id.toCoordinates()}' in file '$relativePath' sets the concluded license " +
                                "to '${curation.data.concludedLicense}'."
                    }

                    curation.data.declaredLicenseMapping.forEach { (source, target) ->
                        runCatching {
                            target.validate(SpdxExpression.Strictness.ALLOW_CURRENT)
                        }.onFailure {
                            issues += "The declared license mapping for package '${curation.id.toCoordinates()}' in " +
                                    "file '$relativePath' maps '$source' to '$target', but '$target' is not a valid " +
                                    "SPDX license expression: ${it.message}"
                        }
                    }

                    val expectedPath = curation.id.toCurationPath()
                    if (relativePath != expectedPath) {
                        issues += "The curation for package '${curation.id.toCoordinates()}' is in the wrong file " +
                                "'$relativePath'. The expected file is '$expectedPath'."
                    }
                }
            }.onFailure { e ->
                issues += "Could not parse curations from file '$relativePath': ${e.message}"
            }
        }

        if (issues.isNotEmpty()) {
            throw GradleException(
                "Found ${issues.size} curation issue(s) in $fileCount package curation file(s) containing " +
                        "$curationCount curation(s):\n${issues.joinToString("\n")}"
            )
        } else {
            logger.quiet(
                "Successfully verified $fileCount package curation file(s) containing $curationCount curation(s)."
            )
        }
    }
}

private fun String.hasVersionRangeIndicators() = versionRangeIndicators.any { contains(it, ignoreCase = true) }

private val versionRangeIndicators = listOf(",", "~", "*", "+", ">", "<", "=", " - ", "^", ".x", "||")
