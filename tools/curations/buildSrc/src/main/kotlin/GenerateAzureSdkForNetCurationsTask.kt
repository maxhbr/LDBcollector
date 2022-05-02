package org.ossreviewtoolkit.tools.curations

import org.gradle.api.tasks.TaskAction
import org.ossreviewtoolkit.model.Identifier

abstract class GenerateAzureSdkForNetCurationsTask : AbstractGenerateCurationsTask() {
    @TaskAction
    fun generate() {
        getFilesFromRepository(owner = "Azure", repository = "azure-sdk-for-net")
            .filter { it.startsWith("sdk/") && it.endsWith(".sln") && "Azure." in it }
            .forEach {
                val project = it.substringAfterLast("/").removeSuffix(".sln")
                val path = it.substringBeforeLast("/")
                val id = Identifier("NuGet::$project")

                createPathCuration(id, path)
            }
    }
}
