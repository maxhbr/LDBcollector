package org.ossreviewtoolkit.tools.curations

import org.gradle.api.DefaultTask
import org.gradle.api.tasks.TaskAction

open class GenerateLicenseClassificationsTask : DefaultTask() {
    init {
        group = "generate license classifications"
        description = "Generates 'license-classifications.yml' from ScanCode's license database available hosted at " +
                "https://scancode-licensedb.aboutcode.org."
    }

    @TaskAction
    fun generate() {
        project.rootDir.resolve("../../license-classifications.yml").apply {
            writeText(generateLicenseClassificationsYaml())
            logger.quiet("Wrote license classifications to '$absolutePath'.")
        }
    }
}
