import com.fasterxml.jackson.dataformat.yaml.YAMLFactory
import com.fasterxml.jackson.dataformat.yaml.YAMLGenerator
import com.fasterxml.jackson.dataformat.yaml.YAMLMapper
import okhttp3.OkHttpClient
import okhttp3.Request
import org.ossreviewtoolkit.model.Identifier
import org.ossreviewtoolkit.model.PackageCuration
import org.ossreviewtoolkit.model.PackageCurationData
import org.ossreviewtoolkit.model.VcsInfoCurationData
import org.ossreviewtoolkit.model.jsonMapper
import org.ossreviewtoolkit.model.mapperConfig
import org.ossreviewtoolkit.utils.common.encodeOr
import org.ossreviewtoolkit.utils.common.safeMkdirs

val githubUsername: String by project
val githubToken: String by project

val mapper = YAMLMapper(YAMLFactory().disable(YAMLGenerator.Feature.WRITE_DOC_START_MARKER)).apply(mapperConfig)

buildscript {
    repositories {
        mavenCentral()
        maven("https://jitpack.io")
    }

    dependencies {
        classpath("com.squareup.okhttp3:okhttp:4.9.3")
        classpath("com.github.oss-review-toolkit.ort:model:65a15f1a14")
    }
}

tasks.register("generateAzureSdkForNetCurations") {
    group = "generate curations"

    doLast {
        getFilesFromRepository(owner = "Azure", repository = "azure-sdk-for-net")
            .filter { it.startsWith("sdk/") && it.endsWith(".sln") && it.contains("Azure.") }
            .forEach {
                val project = it.substringAfterLast("/").removeSuffix(".sln")
                val path = it.substringBeforeLast("/")
                val id = Identifier("NuGet::$project")

                createPathCuration(id, path)
            }
    }
}

fun getFilesFromRepository(
    owner: String,
    repository: String,
    ref: String = "main"
): List<String> {
    val client = OkHttpClient()

    val request =
        Request.Builder()
            .url("https://api.github.com/repos/$owner/$repository/git/trees/$ref?recursive=1")
            .header(
                "Authorization",
                okhttp3.Credentials.basic(githubUsername, githubToken)
            )
            .build()

    return client.newCall(request).execute().use { response ->
        if (!response.isSuccessful) throw java.io.IOException("${response.code} - ${response.message}")

        val json = jsonMapper.readTree(response.body!!.string())
        json["tree"].map { it["path"].textValue() }
    }
}

fun createPathCuration(id: Identifier, path: String) {
    println("Creating path curation for id=${id.toCoordinates()} path=$path.")

    val curation = PackageCuration(
        id = id,
        data = PackageCurationData(
            comment = "Set the VCS path of the module inside the multi-module repository.",
            vcs = VcsInfoCurationData(
                path = path
            )
        )
    )

    val file = rootDir.resolve("../../curations/${id.toCurationPath()}")
    file.parentFile.safeMkdirs()
    mapper.writeValue(file, listOf(curation))
}

fun Identifier.toCurationPath() =
    "${type.encodeOr("_")}/${namespace.encodeOr("_")}/${name.encodeOr("_")}.yml"
