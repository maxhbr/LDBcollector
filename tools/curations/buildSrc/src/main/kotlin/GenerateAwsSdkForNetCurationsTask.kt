package org.ossreviewtoolkit.tools.curations

import org.gradle.api.tasks.TaskAction
import org.ossreviewtoolkit.model.Identifier

open class GenerateAwsSdkForNetCurationsTask : BaseGenerateCurationsTask() {
    private val fourDigitVersionRegex = Regex("""\d+\.\d+\.\d+\.\d+""")

    @TaskAction
    fun generate() {
        val data = mutableSetOf<PathCurationData>()
        val targetFrameworkRegex = Regex("""\.Net.+$""")

        getTagsFromRepository(owner = "aws", repository = "aws-sdk-net")
            .filter { it.isFourDigitVersion() }
            .forEach { tag ->
                logger.quiet("Processing tag $tag.")

                getFilesFromRepository(owner = "aws", repository = "aws-sdk-net", ref = tag)
                    .filter { it.startsWith("sdk/src/Services/") && it.endsWith(".csproj") }
                    .forEach {
                        val project = it.substringAfterLast("/")
                            .removeSuffix(".csproj")
                            .replace(targetFrameworkRegex, "")
                        val path = it.substringBeforeLast("/")
                        val id = Identifier("NuGet::$project")

                        // The AWS SDK for .NET uses a four-part version number for all packages. However, Semver4j
                        // does not support four-part version numbers. Therefore, remove the fourth digit.
                        val threeDigitVersionTag =
                            if (tag.count { c -> c == '.' } == 3) tag.substringBeforeLast(".") else tag

                        if ("AWSSDK." in project) {
                            data += PathCurationData(id, path, threeDigitVersionTag)
                        }
                    }
            }

        data.groupBy { it.id }.forEach { (_, curationData) ->
            curationData.toPathCurations().forEach { saveCuration(it) }
        }
    }

    private fun String.isFourDigitVersion() = fourDigitVersionRegex.matches(this)
}
