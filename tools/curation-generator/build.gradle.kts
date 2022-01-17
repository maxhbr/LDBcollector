import com.fasterxml.jackson.dataformat.yaml.YAMLFactory
import com.fasterxml.jackson.dataformat.yaml.YAMLGenerator
import com.fasterxml.jackson.dataformat.yaml.YAMLMapper
import com.fasterxml.jackson.module.kotlin.readValue
import okhttp3.OkHttpClient
import okhttp3.Request
import org.ossreviewtoolkit.model.Identifier
import org.ossreviewtoolkit.model.PackageCuration
import org.ossreviewtoolkit.model.PackageCurationData
import org.ossreviewtoolkit.model.VcsInfoCurationData
import org.ossreviewtoolkit.model.jsonMapper
import org.ossreviewtoolkit.model.mapper
import org.ossreviewtoolkit.model.mapperConfig
import org.ossreviewtoolkit.utils.common.encodeOr
import org.ossreviewtoolkit.utils.common.safeMkdirs

val githubUsername: String by project
val githubToken: String by project

val curationsDir = rootDir.resolve("../../curations")
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
            .filter { it.startsWith("sdk/") && it.endsWith(".sln") && "Azure." in it }
            .forEach {
                val project = it.substringAfterLast("/").removeSuffix(".sln")
                val path = it.substringBeforeLast("/")
                val id = Identifier("NuGet::$project")

                createPathCuration(id, path)
            }
    }
}

tasks.register("generateDotNetRuntimeCurations") {
    group = "generate curations"

    doLast {
        getFilesFromRepository(owner = "dotnet", repository = "runtime")
            .filter { it.startsWith("src/libraries/") && it.endsWith(".sln") }
            .forEach {
                val project = it.substringAfterLast("/").removeSuffix(".sln")
                val path = it.substringBeforeLast("/")
                val id = Identifier("NuGet::$project")

                if ("System." in project || "Microsoft." in project) {
                    createPathCuration(id, path)
                }
            }
    }
}

tasks.register("generateAspNetCoreCurations") {
    group = "generate curations"

    doLast {
        getFilesFromRepository(owner = "dotnet", repository = "aspnetcore")
            .filter { it.startsWith("src/") && it.endsWith(".csproj") }
            .forEach {
                val project = it.substringAfterLast("/").removeSuffix(".csproj")
                val path = it.substringBeforeLast("/")
                val id = Identifier("NuGet::$project")
                if (project.startsWith("Microsoft.") && !project.endsWith("Tests") && !project.endsWith("Test")) {
                    createPathCuration(id, path)
                }
            }
    }
}

tasks.register("verifyPackageCurations") {
    group = "verification"

    doLast {
        var count = 0
        val issues = mutableListOf<String>()

        curationsDir.walk().filter { it.isFile }.forEach { file ->
            val relativePath = file.relativeTo(curationsDir).invariantSeparatorsPath

            runCatching {
                if (file.extension != "yml") {
                    issues += "The file '$relativePath' does not use the expected extension '.yml'."
                }

                val curations = file.mapper().readValue<List<PackageCuration>>(file)

                if (curations.isEmpty()) {
                    issues += "The file '$relativePath' does not contain any curations."
                }

                curations.forEach { curation ->
                    if (curation.id.name.isBlank()) {
                        issues += "Only curations for specific packages are allowed, but the curation for package " +
                                "'${curation.id.toCoordinates()}' in file '$relativePath' does not have a package name."
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

                    if (curation.data.declaredLicenseMapping.isNotEmpty()) {
                        issues += "Curating declared licenses is not allowed, but the curation for package " +
                                "'${curation.id.toCoordinates()}' in file '$relativePath' sets the declared license " +
                                "mapping to '${curation.data.declaredLicenseMapping}'."
                    }

                    val expectedPath = curation.id.toCurationPath()
                    if (relativePath != expectedPath) {
                        issues += "The curation for package '${curation.id.toCoordinates()}' is in the wrong file " +
                                "'$relativePath'. The expected file is '$expectedPath'."
                    }
                }
            }.onSuccess {
                ++count
            }.onFailure { e ->
                issues += "Could not parse curations from file '$relativePath': ${e.message}"
            }

        }

        if (issues.isNotEmpty()) {
            throw GradleException("Found ${issues.size} curation issues:\n${issues.joinToString("\n")}")
        } else {
            println("Successfully verified $count package curations.")
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

    val file = curationsDir.resolve(id.toCurationPath())
    file.parentFile.safeMkdirs()
    mapper.writeValue(file, listOf(curation))
}

fun Identifier.toCurationPath() =
    "${type.encodeOr("_")}/${namespace.encodeOr("_")}/${name.encodeOr("_")}.yml"
