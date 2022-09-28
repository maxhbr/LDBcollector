package org.ossreviewtoolkit.tools.curations

import org.gradle.api.tasks.TaskAction
import org.ossreviewtoolkit.model.Identifier

open class GenerateAspNetCoreCurationsTask : BaseGenerateCurationsTask() {
    @TaskAction
    fun generate() {
        val data = mutableListOf<PathCurationData>()

        getTagsFromRepository(owner = "dotnet", repository = "aspnetcore")
            .filter { it.isVersion() }
            .forEach { tag ->
                logger.quiet("Processing tag $tag.")

                getFilesFromRepository(owner = "dotnet", repository = "aspnetcore", ref = tag)
                    .filter { it.startsWith("src/") && it.endsWith(".csproj") }
                    .forEach {
                        val project = it.substringAfterLast("/").removeSuffix(".csproj")
                        val path = it.substringBeforeLast("/")
                        if (
                            project.startsWith("Microsoft.")
                            && !project.endsWith("Tests")
                            && !project.endsWith("Test")
                            && !path.endsWith("/ref")
                        ) {
                            val id = Identifier("NuGet::$project")
                            data += PathCurationData(id, path, tag)
                        }
                    }
            }

        data.groupBy { it.id }.forEach { (_, curationData) ->
            curationData.toPathCurations().forEach { saveCuration(it) }
        }
    }
}
