package org.ossreviewtoolkit.tools.curations

import com.fasterxml.jackson.module.kotlin.readValue
import org.gradle.api.DefaultTask
import org.gradle.api.GradleException
import org.gradle.api.tasks.TaskAction
import org.ossreviewtoolkit.model.config.PackageConfiguration
import org.ossreviewtoolkit.model.mapper

open class VerifyPackageConfigurationsTask : DefaultTask() {
    init {
        group = "verification"
    }

    @TaskAction
    fun verify() {
        var fileCount = 0
        val issues = mutableListOf<String>()

        packageConfigurationsDir.walk().filter { it.isFile }.forEach { file ->
            fileCount++

            val relativePath = file.relativeTo(packageConfigurationsDir).invariantSeparatorsPath

            runCatching {
                if (file.extension != "yml") {
                    issues += "The file '$relativePath' does not use the expected extension '.yml'."
                }

                val config = file.mapper().readValue<PackageConfiguration>(file)

                if (config.id.name.isBlank()) {
                    issues += "Only package configurations for specific packages are allowed, but the configuration " +
                            "for package '${config.id.toCoordinates()} in file '$relativePath' does not have a " +
                            "package name."
                }

                if (config.id.version.isBlank()) {
                    issues += "Only package configurations for specific versions are allowed, but the configuration " +
                            "for package '${config.id.toCoordinates()}' in file '$relativePath' does not have a " +
                            "version."
                }

                config.sourceArtifactUrl?.run {
                    if (isBlank()) {
                        issues += "Package configurations must set a valid source artifact URL, but the " +
                                "configuration for package '${config.id.toCoordinates()}' in file '$relativePath' " +
                                "is blank."
                    }
                }

                config.vcs?.run {
                    if (revision == null || revision?.isBlank() == true) {
                        issues += "Package configurations with a VCS matcher must set a revision, but the " +
                                "configuration for package '${config.id.toCoordinates()}' in file '$relativePath' " +
                                "does not set a revision."
                    }
                }

                if (config.licenseFindingCurations.isEmpty() && config.pathExcludes.isEmpty()) {
                    issues += "The package configuration for package '${config.id.toCoordinates()}' in file " +
                            "'$relativePath' does not define any license finding curations or path excludes."
                }

                val expectedPath = config.expectedPath()
                if (relativePath != expectedPath) {
                    issues += "The configuration for package '${config.id.toCoordinates()}' is in the wrong file " +
                            "'$relativePath'. The expected file is '$expectedPath'."
                }
            }.onFailure { e ->
                issues += "Could not parse package configurations from file '$relativePath': ${e.message}"
            }
        }

        if (issues.isNotEmpty()) {
            throw GradleException(
                "Found ${issues.size} package configuration issue(s) in $fileCount package configuration file(s):\n" +
                        issues.joinToString("\n")
            )
        } else {
            logger.quiet(
                "Successfully verified $fileCount package configuration file(s)."
            )
        }
    }
}
