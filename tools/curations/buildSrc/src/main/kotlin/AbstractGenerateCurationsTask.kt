package org.ossreviewtoolkit.tools.curations

import com.fasterxml.jackson.dataformat.yaml.YAMLFactory
import com.fasterxml.jackson.dataformat.yaml.YAMLGenerator
import com.fasterxml.jackson.dataformat.yaml.YAMLMapper
import com.fasterxml.jackson.module.kotlin.readValue
import okhttp3.Credentials
import okhttp3.OkHttpClient
import okhttp3.Request
import org.gradle.api.DefaultTask
import org.gradle.kotlin.dsl.provideDelegate
import org.ossreviewtoolkit.model.Identifier
import org.ossreviewtoolkit.model.PackageCuration
import org.ossreviewtoolkit.model.PackageCurationData
import org.ossreviewtoolkit.model.VcsInfoCurationData
import org.ossreviewtoolkit.model.jsonMapper
import org.ossreviewtoolkit.model.mapperConfig
import org.ossreviewtoolkit.utils.common.safeMkdirs
import java.io.IOException

open class AbstractGenerateCurationsTask : DefaultTask() {
    private val githubUsername: String by project
    private val githubToken: String by project

    private val mapper =
        YAMLMapper(YAMLFactory().disable(YAMLGenerator.Feature.WRITE_DOC_START_MARKER)).apply(mapperConfig)

    private val httpClient = OkHttpClient()

    init {
        group = "generate curations"
    }

    private fun gitHubRequestBuilder() =
        Request.Builder().header("Authorization", Credentials.basic(githubUsername, githubToken))

    fun getFilesFromRepository(
        owner: String,
        repository: String,
        ref: String = "main"
    ): List<String> {
        val request = gitHubRequestBuilder()
            .url("https://api.github.com/repos/$owner/$repository/git/trees/$ref?recursive=1")
            .build()

        return httpClient.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("${response.code} - ${response.message}")

            val json = jsonMapper.readTree(response.body!!.string())
            json["tree"].map { it["path"].textValue() }
        }
    }

    fun getTagsFromRepository(
        owner: String,
        repository: String
    ): List<String> {
        val request = gitHubRequestBuilder()
            .url("https://api.github.com/repos/$owner/$repository/git/refs/tags")
            .build()

        return httpClient.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("${response.code} - ${response.message}")

            val json = jsonMapper.readTree(response.body!!.string())
            json.map { it["ref"].textValue().removePrefix("refs/tags/") }
        }
    }

    fun createPathCuration(id: Identifier, path: String) {
        logger.quiet("Creating path curation for id=${id.toCoordinates()} path=$path.")

        val curation = PackageCuration(
            id = id,
            data = PackageCurationData(
                comment = "Set the VCS path of the module inside the multi-module repository.",
                vcs = VcsInfoCurationData(
                    path = path
                )
            )
        )

        saveCuration(curation)
    }

    fun saveCuration(curation: PackageCuration) {
        val file = curationsDir.resolve(curation.id.toCurationPath())
        file.parentFile.safeMkdirs()

        val existingCurations = if (file.isFile) {
            mapper.readValue<List<PackageCuration>>(file).toMutableList()
        } else {
            mutableListOf()
        }

        // Remove existing curations for the same version with the same comment, but keep the others.
        existingCurations.removeAll { it.id == curation.id && it.data.comment == curation.data.comment }
        existingCurations += curation

        mapper.writeValue(file, existingCurations.sortedBy { it.id })
    }
}
