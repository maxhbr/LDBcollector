package org.ossreviewtoolkit.tools.curations

import org.gradle.api.tasks.TaskAction
import org.ossreviewtoolkit.plugins.packagemanagers.nuget.utils.getIdentifierWithNamespace

open class GenerateAzureSdkForNetCurationsTask : BaseGenerateCurationsTask() {
    @TaskAction
    fun generate() {
        getFilesFromRepository(owner = "Azure", repository = "azure-sdk-for-net")
            .filter { it.startsWith("sdk/") && it.endsWith(".sln") && "Azure." in it }
            .forEach {
                val project = it.substringAfterLast("/").removeSuffix(".sln")
                val path = it.substringBeforeLast("/")
                val id = getIdentifierWithNamespace("NuGet", project, "")

                createPathCuration(id, path)
            }
    }
}
