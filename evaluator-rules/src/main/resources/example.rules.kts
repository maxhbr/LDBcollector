/*
 * Copyright (C) 2019-2022 HERE Europe B.V.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * SPDX-License-Identifier: Apache-2.0
 * License-Filename: LICENSE
 */

/*******************************************************
 * Example OSS Review Toolkit (ORT) .rules.kts file    *
 *                                                     *
 * Note this file only contains example how to write   *
 * rules. It's recommended you consult your own legal  *
 * when writing your own rules.                        *
 *******************************************************/

/**
 * Variables defining the organization using ORT.
 */
val orgName = "Example Inc."
val orgScanIssueTrackerName = "FOSS JIRA"
val orgScanIssueTrackerMdLink = "[$orgScanIssueTrackerName](https://jira.example.com/FOSS)"

/**
 * Import the license classifications from license-classifications.yml.
 */

val copyleftLicenses = licenseClassifications.licensesByCategory["copyleft"].orEmpty()

val copyleftLimitedLicenses = licenseClassifications.licensesByCategory["copyleft-limited"].orEmpty()

val permissiveLicenses = licenseClassifications.licensesByCategory["permissive"].orEmpty()

val publicDomainLicenses = licenseClassifications.licensesByCategory["public-domain"].orEmpty()

/**
 * The complete set of licenses covered by policy rules.
 */
 val handledLicenses = listOf(
    permissiveLicenses,
    publicDomainLicenses,
    copyleftLicenses,
    copyleftLimitedLicenses
).flatten().let {
    it.getDuplicates().let { duplicates ->
        require(duplicates.isEmpty()) {
            "The classifications for the following licenses overlap: $duplicates"
        }
    }

    it.toSet()
}

/**
 * List of licenses approved by organization to be used for its open source projects.
 */
val OrgOssProjectsApprovedLicenses = listOf(
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "MIT"
).map { it.toSpdx() as SpdxSingleLicenseExpression }.toSortedSet(compareBy { it.toString() })

/**
 * Variables used to generate MarkDown text of howToFixDefault()
 */
var doNotWorryText = "_Note_: Do not worry about creating a perfect curation or exclude. Reviewers will provide feedback."
val globTutorialMdLink = "[reference documentation](https://docs.oracle.com/javase/tutorial/essential/io/fileOps.html#glob)"
val ortConfigContributingMdLink = "[CONTRIBUTING.md](https://github.com/oss-review-toolkit/ort-config/blob/main/CONTRIBUTING.md)"
val ortConfigVcsMdLink = "[ort-config repository](https://github.com/oss-review-toolkit/ort-config)"
val ortCurationsYmlFileConcludedLicenseMdLink = "[concluded license curation](https://github.com/oss-review-toolkit/ort/blob/main/docs/config-file-curations-yml.md)"
val ortCurationsYmlFileDeclaredLicenseMdLink = "[declared license curation](https://github.com/oss-review-toolkit/ort/blob/main/docs/config-file-curations-yml.md)"
val ortCurationsYmlVcsPathMdLink = "[VCS path curation](https://github.com/oss-review-toolkit/ort/blob/main/docs/config-file-curations-yml.md)"
val ortCurationsYmlVcsUrlMdLink = "[VCS URL curation](https://github.com/oss-review-toolkit/ort/blob/main/docs/config-file-curations-yml.md)"
var ortLicenseFindingCurationReasonMdLink = "[LicenseFindingCurationReason.kt](https://github.com/oss-review-toolkit/ort/blob/main/model/src/main/kotlin/config/LicenseFindingCurationReason.kt)"
val ortPackageConfigurationFileMdLink = "[package configuration](https://github.com/oss-review-toolkit/ort/blob/main/docs/config-file-package-configuration-yml.md)"
var ortPathExcludeReasonMdLink = "[PathExcludeReason.kt](https://github.com/oss-review-toolkit/ort/blob/main/model/src/main/kotlin/config/PathExcludeReason.kt)"
val ortResolutionsYmlRuleViolationMdLink = "[rule violation resolution](https://github.com/oss-review-toolkit/ort/blob/main/docs/config-file-resolutions-yml.md#resolving-policy-rule-violations)"
val ortScopeExcludeReasonMdLink = "[ScopeExcludeReason.kt](https://github.com/oss-review-toolkit/ort/blob/main/model/src/main/kotlin/config/ScopeExcludeReason.kt)"
val ortYmlFileMdLink = "[.ort.yml file](https://github.com/oss-review-toolkit/ort/blob/main/docs/config-file-ort-yml.md)"
val ortYmlFilePathExcludeMdLink = "[path exclude](https://github.com/oss-review-toolkit/ort/blob/main/docs/config-file-ort-yml.md#excluding-paths)"
val ortYmlFileScopeExcludeMdLink = "[scope exclude](https://github.com/oss-review-toolkit/ort/blob/main/docs/config-file-ort-yml.md#excluding-scopes)"
val ortYmlFileLicenseFindingCurationMdLink = "[license finding curation](https://github.com/oss-review-toolkit/ort/blob/main/docs/config-file-ort-yml.md#curations)"
val ortYmlFileRuleViolationResolutionMdLink = "[rule violation resolution](https://github.com/oss-review-toolkit/ort/blob/main/docs/config-file-ort-yml.md#resolutions)"
val relatesToIssueText = "Relates-to: [Insert related issue number]".takeIf { ortResult.labels["jira"].isNullOrEmpty() } ?: "Relates-to: ${ortResult.labels["jira"]}"

enum class PolicyRules() {
    OSS_PROJECT,
    PROPRIETARY_PROJECT
}

fun getArtifactOrUrlName(url: String): String =
    "name of the artifact".takeIf { url.isNullOrBlank() } ?: "${url.substringAfterLast("/")}"

fun getArtifactMavenSourcesMdLink(pkg: Package): String {
    if (pkg.binaryArtifact.url.isNullOrEmpty()) return "URL of the binary"

    val binaryUrl = pkg.binaryArtifact.url
    val binaryName = binaryUrl.substringAfterLast("/").substringBeforeLast(".")
    val sourcesName = binaryName.plus("-sources")
    val sourcesUrl = binaryUrl.replace(binaryName, sourcesName)

    return "[$sourcesName.jar]($sourcesUrl)"
}

fun getArtifactMdLink(url: String): String =
    "URL of the artifact".takeIf { url.isNullOrBlank() } ?: "[${url.substringAfterLast("/")}]($url)"

/**
 * Return set of policy rules based on project label passed to ORT.
 */
fun getEnabledPolicyRules(): PolicyRules =
    when {
        isLabeled("project", "oss-project") -> PolicyRules.OSS_PROJECT
        else -> PolicyRules.PROPRIETARY_PROJECT
    }

/**
 * Return file path of package configuration in the ORT configuration repository for package [id]. 
 *
 * For example, if 'PyPI::flower:0.9.7' is found in your scan,
 * then this function will return: 'package-configurations/PyPI/_/flower/0.9.7/vcs.yml'
 *
 */
fun getPackageConfigurationFilePath(id: Identifier): String =
    "package-configurations/${id.toPath(emptyValue = "_")}/"

/**
 * Return the package configuration matcher for package [id]. 
 *
 * For example, if 'PyPI::flower:0.9.7' is found in your scan,
 * then this function will return:
 *
 * id: "PyPI::flower:0.9.7"
 * vcs:
 *   type: "Git"
 *   url: "https://github.com/mher/flower.git"
 *   revision: "26d19a816a362cdce32fd125596ed3bd238b40b4"
 *
 */
fun getPackageConfigurationMatcherText(id: Identifier): String {
    if (!ortResult.isPackage(id)) return "|"

    val provenance = ortResult.getScanResultsForId(id).firstOrNull()?.provenance

    if (provenance is ArtifactProvenance) {
        return """
        |   id: "${id.toCoordinates()}"
        |   source_artifact_url: "${provenance.sourceArtifact.url}"
        """.trim()
    }

    if (provenance is RepositoryProvenance) {
        val vcsInfo = provenance.vcsInfo

        return buildString {
            """
            |   id: "${id.toCoordinates()}"
            |   vcs:
            |     type: "${vcsInfo.type}"
            |     url: "${vcsInfo.url}"
            |     revision: "${provenance.resolvedRevision}"
            """.trim().let{ appendLine(it) }

            """
            |     path: "${vcsInfo.path}"
            """.trim().takeIf { vcsInfo.type == VcsType.GIT_REPO }?.let { appendLine(it) }
        }.trim()
    }

    return "|"
}

/**
 * Return the file path within ORT's configuration curations directory for [id].
 *
 * For example, if 'NPM::acorn:7.1.1' is found in your scan,
 * then this function will return 'curations/NPM/_/acorn.yml'.
 *
 */
fun getPackageCurationsFilePath(id: Identifier): String =
    "curations/${id.type}/${id.namespace.ifBlank { "_" }}/${id.name}.yml"

/**
 * Return a MarkDown link to the code repository for package [pkg]. 
 */
fun getVcsMdLink(pkg: Package) : String {
    if (pkg.vcsProcessed.url.isNullOrEmpty()) {
         return "URL of the source code repository"
    }

    val vcsUrl = pkg.vcsProcessed.url.replaceCredentialsInUri()

    return "[${vcsUrl.substringAfterLast("/")} repository](${vcsUrl.replace("ssh", "http")})"
}

/**
 * Return true if [license] is on the list of the organization's approved licenses for its open source projects.
 */
fun isApprovedOrgOssProjectLicense(license: SpdxSingleLicenseExpression) = license in OrgOssProjectsApprovedLicenses

/**
 * Return true if a label with identical [key] exists whose comma separate values contains [value].
 */
fun isLabeled(key: String, value: String) =
    ortResult.labels[key]?.split(",")?.map { it.trim() }?.contains(value) == true

/**
 * Return true if the [ortResult] contains a scan result for the source artifact of the package denoted by [id].
 */
fun isSourceArtifactScanned(id: Identifier): Boolean =
    ortResult.getScanResultsForId(id).any { it.provenance is ArtifactProvenance }

/**
 * Return true if the [ortResult] contains a scan result for the VCS of the package denoted by [id].
 */
fun isVcsScanned(id: Identifier): Boolean =
    ortResult.getScanResultsForId(id).any { it.provenance is RepositoryProvenance }

/**
 * Return the coordinates without the version.
 *
 * For example, this function will return 'PyPI:flower' for package id 'PyPI::flower:0.9.7'
 * and 'Maven:org.antlr:antlr4' for 'Maven:org.antlr:antlr4:4.0.0'.
 *
 */
fun Identifier.toCoordinatesWithoutVersion() = "$type:$namespace:$name"

/**
 * Return Markdown-formatted text to aid users with resolving violations.
 */
fun PackageRule.howToFixDefault() = """
        A text written in MarkDown to help users resolve policy violations
        which may link to additional resources.
    """.trimIndent()

fun PackageRule.howToFixLicenseViolationDefault(
    license: String,
    licenseSource: LicenseSource,
    @Suppress("UNUSED_PARAMETER") severity: Severity
): String {
    if (ortResult.isProject(pkg.id)) {
        // Violation is flagged for the project scanned.
        if (licenseSource == LicenseSource.DETECTED) {
            // License is detected by the scanner in the source code of the project.
            return "${resolveViolationInSourceCodeText(pkg, license)}".trimMargin()
        }

        // License is declared in project's package manifest file (pom, package.json, etc.).
        return "For this violation, there is no recommended solution.".trimMargin()
    }

    // Violation is thrown for one of the project's dependencies.
    if (licenseSource == LicenseSource.DETECTED) {
        // Violation thrown for license detected by the scanner in the source code of the dependency.
        return "${resolveViolationInDependencySourceCodeText(pkg, license)}".trimMargin()
    }

    // Violation thrown for declared license in dependency's package manifest file (pom, package.json, etc.).
    return "${resolveViolationInDependencyDeclaredLicenseText(pkg)}".trimMargin()
}

fun PackageRule.howToFixUnhandledLicense(
    license: String,
    licenseSource: LicenseSource,
    @Suppress("UNUSED_PARAMETER") severity: Severity
) : String {
    val createIssueText = """
        |1. If an issue to add this license does not already exist in $orgScanIssueTrackerMdLink, please create it.
        |2. Set the _Summary_ field to 'Add new license $license'.
        |3. Set the _Component/s_ field to _licenses_.
        |4. Set the _Description_ field to something like 'Please add this license to the review tooling.'
        |"""

    if (ortResult.isProject(pkg.id)) {
        // Unhandled license is found in the project under review.
        if (licenseSource == LicenseSource.DETECTED) {
            // Unhandled license is detected by the scanner in the source code of the project.
            return """
                |${resolveViolationInSourceCodeText(pkg, license)}
                |
                |If the license identification is correct and can not be excluded, then
                |follow the steps below to have Open Source Office add $license to the review tooling:
                |
                $createIssueText
                |""".trimMargin()
        }

        // Unhandled license is declared in project's package manifest file (pom, package.json, etc.).
        return """
            |Follow the steps below to have Open Source Office add $license to the review tooling:
            |
            $createIssueText
            |""".trimMargin()
    } else {
        //  Unhandled license is found in project's dependency.
        if (licenseSource == LicenseSource.DETECTED) {
            // Unhandled license is detected by the scanner in the source code of the dependency.
            return """
                |${resolveViolationInDependencySourceCodeText(pkg, license)}
                |
                |If the license identification is correct and can not be excluded, then
                |follow the steps below to add $license to the review tooling:
                |
                $createIssueText
                |""".trimMargin()
        }

        // Unhandled license is declared in dependency's package manifest file (pom, package.json, etc.).
        return """
            |Follow the steps below to add $license to the review tooling:
            |
            $createIssueText
            |""".trimMargin()
    }
}

fun PackageRule.howToFixOssProjectDefault() = """
        A text written in MarkDown to help users resolve policy violations
        which may link to additional resources.
    """.trimIndent()

fun PackageRule.howToFixUnmappedDeclaredLicense(
    license: String,
    @Suppress("UNUSED_PARAMETER") severity: Severity
): String {
    val genericDeclaredLicenses = setOf(
        "BSD License",
        "The BSD License"
    )

    return if (license in genericDeclaredLicenses) {
        val binaryUrlMdLink = getArtifactMdLink(pkg.binaryArtifact.url)
        val vcsUrlMdLink = getVcsMdLink(pkg)

        """
            |Try to resolve this violation by following the advice below:
            |
            |1. Clone $ortConfigVcsMdLink using Git.
            |2. Map declared license '$license' to an [SPDX license expression](https://spdx.github.io/spdx-spec/appendix-IV-SPDX-license-expressions/):
            |   - Open or create using a text editor `${getPackageCurationsFilePath(pkg.id)}`.
            |   - Determine the declared licenses for $binaryUrlMdLink by looking for the main license files in the $vcsUrlMdLink.
            |     Use the the following template, changing the text in square brackets (`[...]`) as appropriate.
            |
            |   ```
            |   - id: "${pkg.id.toCoordinatesWithoutVersion()}"
            |     curations:
            |       comment: "Mapping declared license based on \
            |         [https://url-to-repository/tag-or-revision-for-version-${pkg.id.version}/LICENSE] and \
            |         [https://url-to-repository/tag-or-revision-for-version-${pkg.id.version}/package-metadata-file]."
            |       declared_license_mapping:
            |         "$license": "[SPDX license expression for the declared license.]"
            |   ```
            |
            |   - Submit the above change to the $ortConfigVcsMdLink (see $ortConfigContributingMdLink for guidance) with a commit message as shown below.
            |     Reviewers are set automatically.
            |
            |   ```
            |   curations: Map declared license for ${pkg.id.toCoordinatesWithoutVersion()}
            |
            |   $relatesToIssueText
            |   ```
            |
            |   - Once your $ortCurationsYmlFileDeclaredLicenseMdLink is merged, re-scan to see if the violation has been resolved.
            |""".trimMargin()
    } else {
        """
            |Follow the steps below to add the $license to the review tooling:
            |
            |1. If a ticket to add this license does not already exist in $orgScanIssueTrackerMdLink, please create it.
            |2. Set the _Summary_ field to 'Add new license mapping for license $license'.
            |3. Set the _Component/s_ field to _licenses_.
            |4. Set the _Description_ field to something like 'Please add a new declared license mapping for this license.'
            |""".trimMargin()
    }
}

fun resolveViolationInDependencyDeclaredLicenseText(pkg: Package) : String {
    val sourcesUrlMdLink = when (pkg.id.type) {
        "Maven" -> {getArtifactMavenSourcesMdLink(pkg)}
        "PIP", "PyPI" -> {getArtifactMdLink(pkg.sourceArtifact.url)}
        else -> "the source artifact"
    }

    if (isSourceArtifactScanned(pkg.id) && pkg.binaryArtifact.url.isNotEmpty()) {
        val binaryName = getArtifactOrUrlName(pkg.binaryArtifact.url)
        val binaryUrlMdLink = getArtifactMdLink(pkg.binaryArtifact.url)

        return """
            |Try to resolve this violation by following the advice below:
            |
            |1. Exclude the package scope if the package is not part of the released artifacts:
            |   - Check _Paths_ > _Scope_ for ${pkg.id.toCoordinates()} in `*-scan-report-web-app.html`
            |   - If _Scope_ indicates the package is used for building or testing your code (e.g. 'compile' or 'test'),
            |     exclude it by adding a $ortYmlFileScopeExcludeMdLink to your $ortYmlFileMdLink.
            |
            |2. Otherwise, add a curation for the package if its declared license includes a license choice:
            |   - Clone $ortConfigVcsMdLink using Git.
            |   - Open or create using a text editor `${getPackageCurationsFilePath(pkg.id)}`.
            |   - Find the licenses applicable to $binaryUrlMdLink by comparing its contents with the scan results for $sourcesUrlMdLink.
            |     (A license does not apply if the scan results show it to be in a particular file, but that file is absent in $binaryUrlMdLink.)
            |   - For each license that applies, create an entry for ${pkg.id.toCoordinates()} in `${getPackageCurationsFilePath(pkg.id)}`, setting  `concluded_license`
            |     to show the appropriate [SPDX license expression](https://spdx.github.io/spdx-spec/appendix-IV-SPDX-license-expressions/).
            |     Use the following template, changing the text in square brackets (`[...]`) as appropriate.
            |
            |   ```
            |   - id: "${pkg.id.toCoordinates()}"
            |     curations:
            |       comment: "[The artifact declares as licensed under '${pkg.declaredLicensesProcessed.spdxExpression}', see \
            |         https://url-to-repository/tag-or-revision-for-version-${pkg.id.version}/LICENSE and \
            |         https://url-to-repository/tag-or-revision-for-version-${pkg.id.version}/package-metadata-file \.
            |         Additionally the scanner detects ...]"
            |       # FIXME: The real concluded license expression, taking into account both declared and detected licenses, is
            |       # concluded_license: "[Applicable licenses for $binaryName as a SPDX license expression.]"
            |       # However, as we do not have a mechanism to record a license choice yet, misuse the concluded
            |       # license to perform the choice until we have a proper mechanism implemented:
            |       concluded_license: "[Chosen licenses for $binaryName as a SPDX license expression.]"
            |   ```
            |
            |   - Submit the above change to the $ortConfigVcsMdLink (see $ortConfigContributingMdLink for guidance) with a commit message as shown below.
            |     Note that reviewers are set automatically.
            |
            |   ```
            |   curations: Conclude license for ${pkg.id.toCoordinates()}
            |
            |   $relatesToIssueText
            |   ```
            |
            |   - Once your $ortCurationsYmlFileConcludedLicenseMdLink is merged, re-scan to see if the violation has been resolved.
            |"""
    }

    val binaryName = getArtifactOrUrlName(pkg.binaryArtifact.url)
    val binaryUrlMdLink = getArtifactMdLink(pkg.binaryArtifact.url)
    val vcsUrlMdLink = getVcsMdLink(pkg)

    if (isVcsScanned(pkg.id) && pkg.binaryArtifact.url.isNotEmpty()) {
        return """
            |Try to resolve this violation by following the advice below:
            |
            |1. Exclude the package scope if the package is not part of the released artifacts:
            |   - Check _Paths_ > _Scope_ for ${pkg.id.toCoordinates()} in `*-scan-report-web-app.html`
            |   - If _Scope_ indicates the package is used for building or testing your code (e.g. 'compile' or 'test'),
            |     exclude it by adding a $ortYmlFileScopeExcludeMdLink to your $ortYmlFileMdLink.
            |
            |2. Otherwise, add a curation for the package if its declared license includes a license choice:
            |   - Clone $ortConfigVcsMdLink using Git.
            |   - Open or create using a text editor `${getPackageCurationsFilePath(pkg.id)}`.
            |   - Find the licenses applicable to $binaryUrlMdLink by comparing its contents with the scan results for $sourcesUrlMdLink.
            |     (A license does not apply if the scan results show it to be in a particular file, but that file is absent in $binaryUrlMdLink.)
            |   - For each license that applies, create an entry for ${pkg.id.toCoordinates()} in `${getPackageCurationsFilePath(pkg.id)}`, setting  `concluded_license`
            |     to show the appropriate [SPDX license expression](https://spdx.github.io/spdx-spec/appendix-IV-SPDX-license-expressions/).
            |     Use the following template, changing the text in square brackets (`[...]`) as appropriate.
            |
            |   ```
            |   - id: "${pkg.id.toCoordinates()}"
            |     curations:
            |       comment: "[The artifact declares as licensed under '${pkg.declaredLicensesProcessed.spdxExpression}', see \
            |         https://url-to-repository/tag-or-revision-for-version-${pkg.id.version}/LICENSE and \
            |         https://url-to-repository/tag-or-revision-for-version-${pkg.id.version}/package-metadata-file \.
            |         Additionally the scanner detects ...]"
            |       # FIXME: The real concluded license expression, taking into account both declared and detected licenses, is
            |       # concluded_license: "[Applicable licenses for $binaryName as SPDX license expression.]"
            |       # However, as we do not have a mechanism to record a license choice yet (see OSS-1163), misuse the concluded
            |       # license to perform the choice until we have a proper mechanism implemented:
            |       concluded_license: "[Chosen licenses for $binaryName as a SPDX license expression.]"
            |   ```
            |
            |   - Submit the above change to the $ortConfigVcsMdLink (see $ortConfigContributingMdLink for guidance) with a commit message as shown below.
            |     Note that reviewers are set automatically.
            |
            |   ```
            |   curations: Conclude license for ${pkg.id.toCoordinates()}
            |
            |   $relatesToIssueText
            |   ```
            |
            |   - Once your $ortCurationsYmlFileConcludedLicenseMdLink is merged, re-scan to see if the violation has been resolved.
            |"""
    } else {
        val vcsName = getArtifactOrUrlName(pkg.vcsProcessed.url)

        return """
            |It may be possible to resolve this violation as follows:
            |
            |1. Try to exclude the scope of the package if it is not part of the released artifacts:
            |   - Check the _Paths_ section for ${pkg.id.toCoordinates()} in the Web App scan report for the scopes where the package was found.
            |   - If a scope is only for packages used for building or testing your code,
            |     exclude it by adding a $ortYmlFileScopeExcludeMdLink to your $ortYmlFileMdLink.
            |
            |2. Otherwise, add a curation for the package if its declared license includes a license choice:
            |   - Clone $ortConfigVcsMdLink using Git.
            |   - Open or create using a text editor `${getPackageCurationsFilePath(pkg.id)}`.
            |   - Find the licenses applicable to $vcsUrlMdLink which are included in your release artifacts.
            |     (A license does not apply if the scan results show it to be in a particular file, but that file is absent in $vcsUrlMdLink).
            |   - For each license that is not compiled in your release artifacts, create an entry for ${pkg.id.toCoordinates()} in `${getPackageCurationsFilePath(pkg.id)}`, setting `concluded_license`
            |     to show the appropriate [SPDX license expression](https://spdx.github.io/spdx-spec/appendix-IV-SPDX-license-expressions/).
            |     Use the following template, changing the text in square brackets (`[...]`) as appropriate.
            |
            |   ```
            |   - id: "${pkg.id.toCoordinates()}"
            |     curations:
            |       comment: "[The artifact declares as licensed under '${pkg.declaredLicensesProcessed.spdxExpression}', see \
            |         https://url-to-repository/tag-or-revision-for-version-${pkg.id.version}/LICENSE and \
            |         https://url-to-repository/tag-or-revision-for-version-${pkg.id.version}/package-metadata-file \.
            |         Additionally the scanner detects ...]"
            |       # FIXME: The real concluded license expression, taking into account both declared and detected licenses, is
            |       # concluded_license: "[Applicable licenses for $vcsName repository as a SPDX license expression.]"
            |       # However, as we do not have a mechanism to record a license choice yet (see OSS-1163), misuse the concluded
            |       # license to perform the choice until we have a proper mechanism implemented:
            |       concluded_license: "[Chosen licenses for $vcsName repository as a SPDX license expression.]"
            |   ```
            |
            |   - Submit the above change to the $ortConfigVcsMdLink (see $ortConfigContributingMdLink for guidance) with a commit message as shown below.
            |     Note that reviewers are set automatically.
            |
            |   ```
            |   curations: Conclude license for ${pkg.id.toCoordinates()}
            |
            |   $relatesToIssueText
            |   ```
            |
            |   - Once your $ortCurationsYmlFileConcludedLicenseMdLink is merged, re-scan to see if the violation has been resolved.
            |"""
    }
}

fun resolveViolationInDependencySourceCodeText(pkg: Package, license: String) : String {
    val sourcesUrlMdLink = when (pkg.id.type) {
        "Maven" -> {getArtifactMavenSourcesMdLink(pkg)}
        "PIP", "PyPI" -> {getArtifactMdLink(pkg.sourceArtifact.url)}
        else -> "the source artifact"
    }

    if (isSourceArtifactScanned(pkg.id) && pkg.binaryArtifact.url.isNotEmpty()) {
        val binaryName = getArtifactOrUrlName(pkg.binaryArtifact.url)
        val binaryUrlMdLink = getArtifactMdLink(pkg.binaryArtifact.url)

        return """
            |Try to resolve this violation by following the advice below:
            |
            |1. Clone $ortConfigVcsMdLink using Git.
            |2. Download and extract:  
            |   - $binaryUrlMdLink
            |   - $sourcesUrlMdLink
            |4. Find the lines which triggered this violation:
            |   - Expand the _Scan Results_ section under ${pkg.id.toCoordinates()} in `*-scan-report-web-app.html`
            |   - Filter the _Value_ column, selecting only the license to which the violation refers
            |5. If there are license file findings for this package in directories in (extracted) $sourcesUrlMdLink but not $binaryUrlMdLink:
            |   - Create a directory `${getPackageConfigurationFilePath(pkg.id)}` with a file named `source-artifact.yml`.
            |   - Open the file `source-artifact.yml` in a text editor
            |   - Add a $ortPackageConfigurationFileMdLink entry with a $ortYmlFilePathExcludeMdLink
            |     for each _directory_ found in the (extracted) $sourcesUrlMdLink but not $binaryUrlMdLink.
            |     Use the following template, changing the text in square brackets (`[...]`) as appropriate.
            |
            |   ```
            |   ---
            ${getPackageConfigurationMatcherText(pkg.id)}
            |   path_excludes:
            |   - pattern: "[A glob pattern matching files or paths.]"
            |     reason: "[One of PathExcludeReason e.g. BUILD_TOOL_OF, DOCUMENTATION_OF, EXAMPLE_OF or TEST_OF.]"
            |   ```
            |
            |     For information on how to write a glob pattern, please see this $globTutorialMdLink.
            |     The available options for the `reason` field are defined in $ortPathExcludeReasonMdLink.
            |
            |   - Submit the above change to the $ortConfigVcsMdLink (see $ortConfigContributingMdLink for guidance) with a commit message as shown below.
            |     Reviewers are set automatically.
            |
            |   ```
            |   packages: Add excludes for ${pkg.id.toCoordinates()}
            |
            |   $relatesToIssueText
            |   ```
            |
            |   - Once your $ortYmlFilePathExcludeMdLink is merged, re-scan to see if the violation has been resolved.
            |
            |6. For each file where the license was found, check if the scanner correctly identified the license.
            |   If a license identification is incorrect:
            |
            |   - Create a directory `${getPackageConfigurationFilePath(pkg.id)}` with a file named `source-artifact.yml`.
            |   - Open `source-artifact.yml` in a text editor.
            |   - Add a $ortPackageConfigurationFileMdLink entry with a $ortYmlFileLicenseFindingCurationMdLink.
            |     Use the following template, changing the text in square brackets (`[...]`) as appropriate.
            |
            |   ```
            |   ---
            ${getPackageConfigurationMatcherText(pkg.id)}
            |   license_finding_curations:
            |   - path: "[A glob pattern matching files or paths.]"
            |     start_lines: "[String with comma-separated list of starting line integers.]"
            |     line_count: [Integer for number of lines to match.]
            |     detected_license: "${license}"
            |     concluded_license: "[SPDX license expression for the correct license or use NONE to remove the detected license.]"
            |     reason: "INCORRECT"
            |     comment: "[A comment explaining why the scanner is incorrect.]"
            |   ```
            |
            |     For information on how to write a glob pattern, visit $globTutorialMdLink.
            |     The available options for the `reason` field are defined in $ortLicenseFindingCurationReasonMdLink.
            |
            |   - Submit the above change to the $ortConfigVcsMdLink (see $ortConfigContributingMdLink for guidance) with a commit message as shown below.
            |     Note that reviewers are set automatically.
            |
            |   ```
            |   packages: Add curations for ${pkg.id.toCoordinates()}
            |
            |   $relatesToIssueText
            |   ```
            |   - Once your $ortYmlFileLicenseFindingCurationMdLink is merged, re-scan to see if the violation has been resolved.
            |            |
            |7. If ${pkg.id.toCoordinates()} includes license choices or a large number of findings to be excluded or curated:
            |   - Open or create using a text editor `${getPackageCurationsFilePath(pkg.id)}`.
            |   - Determine the applicable licenses for $binaryUrlMdLink by comparing its contents with the scan result findings.
            |     (A license does not apply if the scan results show it to be in a particular file, but that file is absent in $binaryUrlMdLink).
            |   - For each license that applies to $binaryUrlMdLink, create an entry for ${pkg.id.toCoordinates()} in `${getPackageCurationsFilePath(pkg.id)}`, setting  `concluded_license`
            |     to show the appropriate [SPDX license expression](https://spdx.github.io/spdx-spec/appendix-IV-SPDX-license-expressions/).
            |     Use the following template, changing the text in square brackets (`[...]`) as appropriate.
            |
            |   ```
            |   - id: "${pkg.id.toCoordinates()}"
            |     curations:
            |       comment: "[The artifact declares as licensed under '${pkg.declaredLicensesProcessed.spdxExpression}', see \
            |         https://url-to-repository/tag-or-revision-for-version-${pkg.id.version}/LICENSE and \
            |         https://url-to-repository/tag-or-revision-for-version-${pkg.id.version}/package-metadata-file \.
            |         Additionally the scanner detects ...]"
            |       concluded_license: "[Applicable licenses for $binaryName as a SPDX license expression.]"
            |   ```
            |
            |   - Submit the above change to the $ortConfigVcsMdLink (see $ortConfigContributingMdLink for guidance) with a commit message as shown below.
            |     Note that reviewers are set automatically.
            |
            |   ```
            |   curations: Conclude license for ${pkg.id.toCoordinates()}
            |
            |   $relatesToIssueText
            |   ```
            |
            |   - Once your $ortCurationsYmlFileConcludedLicenseMdLink is merged, re-scan to see if the violation has been resolved.
            |   - $doNotWorryText
            |"""
    }
    val binaryName = getArtifactOrUrlName(pkg.binaryArtifact.url)
    val binaryUrlMdLink = getArtifactMdLink(pkg.binaryArtifact.url)
    val vcsUrlMdLink = getVcsMdLink(pkg)

    if (isVcsScanned(pkg.id) && pkg.binaryArtifact.url.isNotEmpty()) {
        return """
            |Try to resolve this violation by following the advice below:
            |
            |1. Clone $ortConfigVcsMdLink using Git.
            |2. Download and extract $binaryUrlMdLink.
            |3. Find the lines which triggered this violation:
            !   - Expand the _Scan Results_ section  under ${pkg.id.toCoordinates()} in `*-scan-report-web-app.html`
            |   - Filter the _Value_ column, selecting only the licenses to which the violation refers
            |4. Open the $vcsUrlMdLink in a web browser and find the source code for version `${pkg.id.version}`.
            |5. If the extracted $binaryUrlMdLink contains fewer files or directories than shown under 
            |   the _Scan Results_ for ${pkg.id.toCoordinates()} in `*-scan-report-web-app.html`, you may need to
            |   limit the number of files/directories the scanner scans. For example, if the repository contains other
            |   packages and not just ${pkg.id.toCoordinates()}:
            |   - Open or create using a text editor `${getPackageCurationsFilePath(pkg.id)}`.
            |   - Add an entry for `${pkg.id.toCoordinates()}` setting the `path` under `vcs`
            |     to the repository directory that contains the source code for the $binaryUrlMdLink.
            |     (To find the correct directory, search the names of files in the extracted $binaryUrlMdLink within $vcsUrlMdLink.)
            |     Use the following template, replacing the `path` field as appropriate.
            |
            |   ```
            |   - id: "${pkg.id.toCoordinatesWithoutVersion()}"
            |     curations:
            |       comment: "Package resides in its own directory within repo."
            |       vcs:
            |         path: "[File path to package e.g. ${pkg.id.name}.]"
            |   ```
            |
            |   - Submit the above change to the $ortConfigVcsMdLink (see $ortConfigContributingMdLink for guidance) with a commit message as shown below.
            |     Reviewers are set automatically.
            |
            |   ```
            |   curations: Set VCS path for ${pkg.id.toCoordinatesWithoutVersion()}
            |
            |   $relatesToIssueText
            |   ```
            |
            |   - Once your $ortCurationsYmlVcsUrlMdLink is merged, re-scan to see if the violation has been resolved.
            |
            |6. If there are license file findings for ${pkg.id.toCoordinates()} in directories in $vcsUrlMdLink but not in the extracted $binaryUrlMdLink:
            |   - Create a directory `${getPackageConfigurationFilePath(pkg.id)}` with a file named `vcs.yml`.
            |   - Open `vcs.yml` in a text editor.
            |   - For each _directory_ found in the $vcsUrlMdLink but not in extracted $binaryUrlMdLink, add a $ortPackageConfigurationFileMdLink entry 
            |     with a $ortYmlFilePathExcludeMdLink.
            |     .
            |     Use the following template, changing the text in square brackets (`[...]`) as appropriate.
            |
            |   ```
            |   ---
            ${getPackageConfigurationMatcherText(pkg.id)}
            |   path_excludes:
            |   - pattern: "[A glob pattern matching files or paths.]"
            |     reason: "[One of PathExcludeReason e.g. BUILD_TOOL_OF, DOCUMENTATION_OF, EXAMPLE_OF or TEST_OF.]"
            |   ```
            |
            |     For information on how to write a glob pattern, please see this $globTutorialMdLink.
            |     The available options for the `reason` field are defined in $ortPathExcludeReasonMdLink.
            |
            |   - Submit the above change to the $ortConfigVcsMdLink (see $ortConfigContributingMdLink for guidance) with a commit message as shown below.
            |     Reviewers are set automatically.
            |
            |   ```
            |   packages: Add excludes for ${pkg.id.toCoordinates()}
            |
            |   $relatesToIssueText
            |   ```
            |
            |   - Once your $ortYmlFilePathExcludeMdLink is merged, re-scan to see if the violation has been resolved.
            |
            |7. For each file where the license was found, check if the scanner correctly identified the license.
            |   If a license identification is incorrect:
            |
            |   - Create a directory `${getPackageConfigurationFilePath(pkg.id)}` with a file named `source-artifact.yml`.
            |   - Open the file `source-artifact.yml` in a text editor.
            |   - Add a $ortPackageConfigurationFileMdLink entry with a $ortYmlFileLicenseFindingCurationMdLink.
            |     Use the following template, changing the text in square brackets (`[...]`) as appropriate.
            |
            |   ```
            |   ---
            ${getPackageConfigurationMatcherText(pkg.id)}
            |   license_finding_curations:
            |   - path: "[A glob pattern matching files or paths.]"
            |     start_lines: "[String with comma-separated list of starting line integers.]"
            |     line_count: [Integer for number of lines to match.]
            |     detected_license: "${license}"
            |     concluded_license: "[SPDX license expression for the correct license or use NONE to remove the detected license.]"
            |     reason: "INCORRECT"
            |     comment: "[A comment explaining why the scanner is incorrect.]"
            |   ```
            |
            |     For information on how to write a glob pattern, please see this $globTutorialMdLink.
            |     The available options for the `reason` field are defined in $ortLicenseFindingCurationReasonMdLink.
            |
            |   - Submit the above change to the $ortConfigVcsMdLink (see $ortConfigContributingMdLink for guidance) with a commit message as shown below.
            |     Reviewers are set automatically.
            |
            |   ```
            |   packages: Add curations for ${pkg.id.toCoordinates()}
            |
            |   $relatesToIssueText
            |   ```
            |
            |   - Once your $ortYmlFileLicenseFindingCurationMdLink is merged, re-scan to see if the violation has been resolved.
            |
            |8. If ${pkg.id.toCoordinates()} includes license choices or a large number of findings to be excluded or curated:
            |   - Open or create using a text editor `${getPackageCurationsFilePath(pkg.id)}`.
            |   - Determine the applicable licenses for $binaryUrlMdLink by comparing its contents with the scan result findings.
            |     (A license does not apply if the scan results show it to be in a particular file, but that file is absent in $binaryUrlMdLink).
            |   - For each license that applies to $binaryUrlMdLink, create an entry for ${pkg.id.toCoordinates()} in `${getPackageCurationsFilePath(pkg.id)}`, setting  `concluded_license`
            |     to show the appropriate [SPDX license expression](https://spdx.github.io/spdx-spec/appendix-IV-SPDX-license-expressions/).
            |     Use the following template, changing the text in square brackets (`[...]`) as appropriate.
            |
            |   ```
            |   - id: "${pkg.id.toCoordinates()}"
            |     curations:
            |       comment: "[The artifact declares as licensed under '${pkg.declaredLicensesProcessed.spdxExpression}', see \
            |         https://url-to-repository/tag-or-revision-for-version-${pkg.id.version}/LICENSE and \
            |         https://url-to-repository/tag-or-revision-for-version-${pkg.id.version}/package-metadata-file \.
            |         Additionally the scanner detects ...]"
            |       concluded_license: "[Applicable licenses for $binaryName as a SPDX license expression.]"
            |   ```
            |
            |   - Submit the above change to the $ortConfigVcsMdLink (see $ortConfigContributingMdLink for guidance) with a commit message as shown below.
            |     Reviewers are set automatically.
            |
            |   ```
            |   curations: Conclude license for ${pkg.id.toCoordinates()}
            |
            |   $relatesToIssueText
            |   ```
            |
            |   - Once your $ortCurationsYmlFileConcludedLicenseMdLink is merged, re-scan to see if the violation has been resolved.
            |   - $doNotWorryText
            |"""
    } else {
        return """
            |Try to resolve this violation by following the advice below:
            |
            |1. Clone $ortConfigVcsMdLink using Git.
            |2. Find the lines which triggered this violation:
            |   - Expand the _Scan Results_ section under ${pkg.id.toCoordinates()} in `*-scan-report-web-app.html`
            |   - Filter the _Value_ column, selecting only the licenses to which the violation refers
            |3. Open the $vcsUrlMdLink in a web browser and find the code for version `${pkg.id.version}`.
            |4. If this package is in a repository containing other packages beside ${pkg.id.toCoordinates()}:
            |   - Open or create using a text editor `${getPackageCurationsFilePath(pkg.id)}`.
            |   - Add an entry for `${pkg.id.toCoordinates()}` setting the `path` under `vcs`
            |     to the repository directory that contains the source code for the package.
            |     Use the following template, changing the value of `path` as appropriate.
            |
            |   ```
            |   - id: "${pkg.id.toCoordinatesWithoutVersion()}"
            |     curations:
            |       comment: "Package resides in its own directory within repo."
            |       vcs:
            |         path: "[File path to package e.g. ${pkg.id.name}.]"
            |   ```
            |
            |   - Submit the above change to the $ortConfigVcsMdLink (see $ortConfigContributingMdLink for guidance) with a commit message as shown below.
            |     Reviewers are set automatically.
            |
            |   ```
            |   curations: Set VCS path for ${pkg.id.toCoordinatesWithoutVersion()}
            |
            |   $relatesToIssueText
            |   ```
            |
            |   - Once your $ortCurationsYmlVcsUrlMdLink is merged, re-scan to see if the violation has been resolved.
            |
            |5. If there are license findings for ${pkg.id.toCoordinates()} in directories in $vcsUrlMdLink used only for building or testing the code:
            |   - Create a directory `${getPackageConfigurationFilePath(pkg.id)}` with a file named `vcs.yml`.
            |   - Open `vcs.yml` in a text editor.
            |   - For each _directory_ found in the $vcsUrlMdLink, but not in extracted $binaryUrlMdLink, add a 
            |     $ortPackageConfigurationFileMdLink entry with a $ortYmlFilePathExcludeMdLink.
            |     Use the following template, changing the text in square brackets (`[...]`) as appropriate.
            |
            |   ```
            |   ---
            ${getPackageConfigurationMatcherText(pkg.id)}
            |   path_excludes:
            |   - pattern: "[A glob pattern matching files or paths.]"
            |     reason: "[One of PathExcludeReason e.g. BUILD_TOOL_OF, DOCUMENTATION_OF, EXAMPLE_OF or TEST_OF.]"
            |   ```
            |
            |     For information on how to write a glob pattern, please see this $globTutorialMdLink.
            |     The available options for the `reason` field are defined in $ortPathExcludeReasonMdLink.
            |
            |   - Submit the above change to the $ortConfigVcsMdLink (see $ortConfigContributingMdLink for guidance) with a commit message as shown below.
            |     Reviewers are set automatically.
            |
            |   ```
            |   packages: Add excludes for ${pkg.id.toCoordinates()}
            |
            |   $relatesToIssueText
            |   ```
            |
            |   - Once your $ortYmlFilePathExcludeMdLink is merged, re-scan to see if the violation has been resolved.
            |
            |6. For each file where the license was found, check if the scanner identified the license correctly.
            |   If a license identification is incorrect:
            |   - Create a directory `${getPackageConfigurationFilePath(pkg.id)}` with a file named `vcs.yml`.
            |   - Open `vcs.yml` in a text editor.
            |   - Add a $ortPackageConfigurationFileMdLink entry with a $ortYmlFileLicenseFindingCurationMdLink.
            |     Use the following template, changing the text in square brackets (`[...]`) as appropriate.
            |
            |   ```
            |   ---
            ${getPackageConfigurationMatcherText(pkg.id)}
            |   license_finding_curations:
            |   - path: "[A glob pattern matching files or paths.]"
            |     start_lines: "[String with comma-separated list of starting line integers.]"
            |     line_count: [Integer for number of lines to match.]
            |     detected_license: "${license}"
            |     concluded_license: "[SPDX license expression for the correct license or use NONE to remove the detected license.]"
            |     reason: "INCORRECT"
            |     comment: "[A comment explaining why the scanner is incorrect.]"
            |   ```
            |
            |     For information on how to write a glob pattern, please see this $globTutorialMdLink.
            |     The available options for the `reason` field are defined in $ortLicenseFindingCurationReasonMdLink.
            |
            |   - Submit the above change to the $ortConfigVcsMdLink (see $ortConfigContributingMdLink for guidance) with a commit message as shown below.
            |     Reviewers are set automatically.
            |
            |   ```
            |   packages: Add curations for ${pkg.id.toCoordinates()}
            |
            |   $relatesToIssueText
            |   ```
            |
            |   - Once your $ortYmlFileLicenseFindingCurationMdLink is merged, re-scan to see if the violation has been resolved.
            |   - $doNotWorryText
            |"""
    }
}

fun resolveViolationInSourceCodeText(pkg: Package, license: String) : String {
    return """
        |Try to resolve this violation by following the advice below:
        |
        |1. Find the lines which triggered this violation:
        |   - expand the _Scan Results_ section under ${pkg.id.toCoordinates()} in `*-web-app.html`
        |   - filter the _Value_ column, selecting only the license to which the violation refers.
        |2. Try to exclude the files or directories to which the violation refers but which are not part of the release artifacts
        |   of your project by adding a $ortYmlFilePathExcludeMdLink to your $ortYmlFileMdLink.
        |
        |3. For each file finding for the license, verify if the scanner correctly identified the license.
        |   If a license identification is incorrect:
        |
        |   - Open your $ortYmlFileMdLink in a text editor.
        |   - Add a $ortYmlFileLicenseFindingCurationMdLink.
        |     Use the following template, changing the text surrounded by square brackets (`[...]`) as appropriate.
        |
        |   ```
        |   ---
        |   curations:
        |     license_findings:
        |     - path: "[A glob pattern matching files or paths.]"
        |       start_lines: "[String with comma-separated list of starting line integers.]"
        |       line_count: [Integer for number of lines to match.]
        |       detected_license: "${license}"
        |       concluded_license: "[SPDX license expression for the correct license or use NONE to remove the detected license.]"
        |       reason: "INCORRECT"
        |       comment: "[A comment explaining why the scanner is incorrect.]"
        |   ```
        |
        |   - Once your $ortYmlFileLicenseFindingCurationMdLink is merged, re-scan to see if the violation has been resolved.
        |"""
}

/**
 * Set of matchers to help keep policy rules easy to understand
 */

fun PackageRule.hasDefinitionFileName(vararg definitionFileNames: String) =
    object : RuleMatcher {
        private val matchingNames = definitionFileNames.toSet()

        override val description = "hasDefinitionFileName(${matchingNames.joinToString()})"

        override fun matches(): Boolean {
            val project = ortResult.getProject(pkg.id)
            if (project == null) return false

            return project.definitionFilePath.substringAfterLast('/') in matchingNames
        }
    }

fun PackageRule.LicenseRule.isApprovedOrgOssProjectLicense() =
    object : RuleMatcher {
        override val description = "isApprovedOrgOssProjectLicense($license)"

        override fun matches() = isApprovedOrgOssProjectLicense(license)
    }

fun PackageRule.LicenseRule.isHandled() =
    object : RuleMatcher {
        override val description = "isHandled($license)"

        override fun matches() =
            license in handledLicenses && ("-exception" !in license.toString() || " WITH " in license.toString())
    }

fun PackageRule.LicenseRule.isCopyleft() =
    object : RuleMatcher {
        override val description = "isCopyleft($license)"

        override fun matches() = license in copyleftLicenses
    }

fun PackageRule.LicenseRule.isCopyleftLimited() =
    object : RuleMatcher {
        override val description = "isCopyleftLimited($license)"

        override fun matches() = license in copyleftLimitedLicenses
    }

fun PackageRule.packageManagerSupportsDeclaredLicenses(): RuleMatcher =
    NoneOf(
        isType("Bundler"),
        isType("DotNet"),
        isType("GoDep"),
        isType("GoMod"),
        isType("Gradle"),
        AllOf(isType("PIP"), Not(hasDefinitionFileName("setup.py"))),
        isType("Pub"),
        isType("Unmanaged")
    )

/**
 * Example policy rules
 */

fun RuleSet.copyleftInDependencyRule() {
    dependencyRule("COPYLEFT_IN_DEPENDENCY") {
        licenseRule("COPYLEFT_IN_DEPENDENCY", LicenseView.CONCLUDED_OR_DECLARED_OR_DETECTED) {
            require {
                +isCopyleft()
            }

            issue(
                Severity.ERROR,
                "The project ${project.id.toCoordinates()} has a dependency licensed under the ScanCode " +
                        "copyleft categorized license $license.",
                howToFixLicenseViolationDefault(license.toString(), licenseSource, Severity.WARNING)
            )
        }
    }
}

fun RuleSet.copyleftLimitedInDependencyRule() {
    dependencyRule("COPYLEFT_LIMITED_IN_DEPENDENCY") {
        require {
            +isAtTreeLevel(0)
            +isStaticallyLinked()
        }

        licenseRule("COPYLEFT_LIMITED_IN_DEPENDENCY", LicenseView.CONCLUDED_OR_DECLARED_OR_DETECTED) {
            require {
                +isCopyleftLimited()
            }

            // Use issue() instead of error() if you want to set the severity.
            issue(
                Severity.WARNING,
                "The project ${project.id.toCoordinates()} has a statically linked direct dependency licensed " +
                        "under the ScanCode copyleft-left categorized license $license.",
                howToFixLicenseViolationDefault(license.toString(), licenseSource, Severity.WARNING)
            )
        }
    }
}

fun RuleSet.copyleftInSourceRule() {
    packageRule("COPYLEFT_IN_SOURCE") {
        require {
            -isExcluded()
        }

        licenseRule("COPYLEFT_IN_SOURCE", LicenseView.CONCLUDED_OR_DECLARED_AND_DETECTED) {
            require {
                -isExcluded()
                +isCopyleft()
            }

            val message = if (licenseSource == LicenseSource.DETECTED) {
                "The ScanCode copyleft categorized license $license was ${licenseSource.name.lowercase()} " +
                        "in package ${pkg.id.toCoordinates()}."
            } else {
                "The package ${pkg.id.toCoordinates()} has the ${licenseSource.name.lowercase()} ScanCode copyleft " +
                        "catalogized license $license."
            }

            error(
                message,
                howToFixLicenseViolationDefault(license.toString(), licenseSource, Severity.ERROR)
            )
        }

        licenseRule("COPYLEFT_LIMITED_IN_SOURCE", LicenseView.CONCLUDED_OR_DECLARED_OR_DETECTED) {
            require {
                -isExcluded()
                +isCopyleftLimited()
            }

            val licenseSourceName = licenseSource.name.lowercase()
            val message = if (licenseSource == LicenseSource.DETECTED) {
                if (pkg.id.type == "Unmanaged") {
                    "The ScanCode copyleft-limited categorized license $license was $licenseSourceName in package " +
                            "${pkg.id.toCoordinates()}."
                } else {
                    "The ScanCode copyleft-limited categorized license $license was $licenseSourceName in package " +
                            "${pkg.id.toCoordinates()}."
                }
            } else {
                "The package ${pkg.id.toCoordinates()} has the $licenseSourceName ScanCode copyleft-limited " +
                        "categorized license $license."
            }

            error(
                message,
                howToFixLicenseViolationDefault(license.toString(), licenseSource, Severity.ERROR)
            )
        }
    }
}

fun RuleSet.deprecatedScopeExludeInOrtYmlRule() {
    ortResultRule("DEPRECATED_SCOPE_EXCLUDE_REASON_IN_ORT_YML") {
        val reasons = ortResult.repository.config.excludes.scopes.mapTo(mutableSetOf()) { it.reason }
        val deprecatedReasons = setOf(ScopeExcludeReason.TEST_TOOL_OF)

        reasons.intersect(deprecatedReasons).forEach { offendingReason ->
            warning(
                "The repository configuration is using the deprecated scope exclude reason '$offendingReason'.",
                "Please use only non-deprecated scope exclude reasons, see " +
                        "https://github.com/oss-review-toolkit/ort/blob/main/model/src/main/" +
                        "kotlin/config/ScopeExcludeReason.kt."
            )
        }
    }
}

fun RuleSet.packageConfigurationInOrtYmlRule() = ortResultRule("PACKAGE_CONFIGURATION_IN_ORT_YML") {
    if (ortResult.repository.config.packageConfigurations.isNotEmpty()) {
        error(
            "The use of package configurations is not allowed in the *.ort.yml file.",
            "Please use a global package configuration in the $ortConfigVcsMdLink."
        )
    }
}

fun RuleSet.packageCurationInOrtYmlRule() = ortResultRule("PACKAGE_CURATION_IN_ORT_YML") {
    if (ortResult.repository.config.curations.packages.isNotEmpty()) {
        error(
            "The use of package curations is not allowed in the *.ort.yml file.",
            "Please use a global package curation in the $ortConfigVcsMdLink."
        )
    }
}

fun RuleSet.vulnerabilityInPackageRule() {
    packageRule("VULNERABILITY_IN_PACKAGE") {
        require {
            -isExcluded()
            +hasVulnerability()
        }

        issue(
            Severity.WARNING,
            "The package ${pkg.id.toCoordinates()} has a vulnerability",
            howToFixDefault()
        )
    }
}

fun RuleSet.vulnerabilityWithHighSeverityInPackageRule() {
    packageRule("HIGH_SEVERITY_VULNERABILITY_IN_PACKAGE") {
        val maxAcceptedSeverity = "5.0"
        val scoringSystem = "CVSS2"

        require {
            -isExcluded()
            +hasVulnerability(maxAcceptedSeverity, scoringSystem) { value, threshold ->
                value.toFloat() >= threshold.toFloat()
            }
        }

        issue(
            Severity.ERROR,
            "The package ${pkg.id.toCoordinates()} has a vulnerability with $scoringSystem severity > " +
                    "$maxAcceptedSeverity",
            howToFixDefault()
        )
    }
}

fun RuleSet.unapprovedOssProjectLicenseRule() = packageRule("UNAPPROVED_OSS_PROJECT_LICENSE") {
    require {
        +isProject()
        +packageManagerSupportsDeclaredLicenses()
    }

    licenseRule("UNAPPROVED_OSS_PROJECT_LICENSE", LicenseView.ONLY_DECLARED) {
        require {
            -isApprovedOrgOssProjectLicense()
        }

        error(
            "Package ${pkg.id.toCoordinates()} declares $license which is not an " +
                    "approved license within $orgName.",
            howToFixOssProjectDefault()
        )
    }
}

fun RuleSet.unhandledLicenseRule() {
    // Define a rule that is executed for each package.
    packageRule("UNHANDLED_LICENSE") {
        // Do not trigger this rule on packages that have been excluded in the .ort.yml.
        require {
            -isExcluded()
        }

        // Define a rule that is executed for each license of the package.
        licenseRule("UNHANDLED_LICENSE", LicenseView.CONCLUDED_OR_DECLARED_AND_DETECTED) {
            require {
                -isExcluded()
                -isHandled()
            }

            // Throw an error message including guidance how to fix the issue.
            error(
                "The license $license is currently not covered by policy rules. " +
                        "The license was ${licenseSource.name.lowercase()} in package " +
                        "${pkg.id.toCoordinates()}",
                howToFixUnhandledLicense(license.toString(), licenseSource, Severity.ERROR)
            )
        }
    }
}

fun RuleSet.unmappedDeclaredLicenseRule() {
    packageRule("UNMAPPED_DECLARED_LICENSE") {
        require {
            -isExcluded()
        }

        resolvedLicenseInfo.licenseInfo.declaredLicenseInfo.processed.unmapped.forEach { unmappedLicense ->
            warning(
                "The declared license '$unmappedLicense' could not be mapped to a valid license or parsed as an SPDX " +
                        "expression. The license was found in package ${pkg.id.toCoordinates()}.",
                howToFixUnmappedDeclaredLicense(unmappedLicense, Severity.WARNING)
            )
        }
    }
}

fun RuleSet.commonRules() {
    unhandledLicenseRule()
    unmappedDeclaredLicenseRule()

    deprecatedScopeExludeInOrtYmlRule()

    packageConfigurationInOrtYmlRule()
    packageCurationInOrtYmlRule()

    vulnerabilityInPackageRule()
    vulnerabilityWithHighSeverityInPackageRule()
}

fun RuleSet.ossProjectRules() {
    unapprovedOssProjectLicenseRule()
}

fun RuleSet.proprietaryProjectRules() {
    copyleftInSourceRule()
    // Define rules that get executed for each dependency of a project:
    copyleftInDependencyRule()
    copyleftLimitedInDependencyRule()
}

val ruleSet = ruleSet(ortResult, licenseInfoResolver, resolutionProvider) {
    commonRules()
    when (getEnabledPolicyRules()) {
        PolicyRules.PROPRIETARY_PROJECT -> proprietaryProjectRules()
        PolicyRules.OSS_PROJECT -> ossProjectRules()
    }
}

// Populate the list of policy rule violations to return.
ruleViolations += ruleSet.violations
