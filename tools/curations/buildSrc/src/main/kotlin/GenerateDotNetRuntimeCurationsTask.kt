package org.ossreviewtoolkit.tools.curations

import org.gradle.api.tasks.TaskAction
import org.ossreviewtoolkit.model.Identifier

open class GenerateDotNetRuntimeCurationsTask : BaseGenerateCurationsTask() {
    @TaskAction
    fun generate() {
        val data = mutableListOf<PathCurationData>()

        getTagsFromRepository(owner = "dotnet", repository = "runtime")
            .filter { it.isVersion() }
            .forEach { tag ->
                logger.quiet("Processing tag $tag.")

                getFilesFromRepository(owner = "dotnet", repository = "runtime", ref = tag)
                    .filter { it.startsWith("src/libraries/") && it.endsWith(".sln") }
                    .forEach {
                        val project = it.substringAfterLast("/").removeSuffix(".sln")
                        val path = it.substringBeforeLast("/")
                        val id = Identifier("NuGet::$project")

                        if ("System." in project || "Microsoft." in project) {
                            data += PathCurationData(id, path, tag)
                        }
                    }
            }

        data.groupBy { it.id }.forEach { (_, curationData) ->
            curationData.toPathCurations().forEach { saveCuration(it) }
        }
    }
}
