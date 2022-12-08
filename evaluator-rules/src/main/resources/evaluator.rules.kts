/*
 * Copyright (C) 2019 The ORT Project Authors (see <https://github.com/oss-review-toolkit/ort-config/blob/main/NOTICE>)
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

/******************************************************************************
 * DISCLAIMER: This file only illustrates how to write evaluator rules, it is *
 *             no recommendation in any way. It is recommended to consult     *
 *             your own legal counsel(s) for setting up your evaluator rules. *
 ******************************************************************************/

/**
 * Variables defining the organization using ORT.
 */
val orgName = "Example Inc."
val orgScanIssueTrackerName = "FOSS JIRA"
val orgScanIssueTrackerMdLink = "[$orgScanIssueTrackerName](https://jira.example.com/FOSS)"

/**
 * Import the license classifications from license-classifications.yml.
 */

fun getLicensesForCategory(category: String): Set<SpdxSingleLicenseExpression> =
    checkNotNull(licenseClassifications.licensesByCategory[category]) {
        "Failed to obtain the license for category '$category', because that category does not exist."
    }

val commercialLicenses = getLicensesForCategory("commercial")
val contributorLicenseAgreementLicenenses = getLicensesForCategory("contributor-license-agreement")
val copyleftLicenses = getLicensesForCategory("copyleft")
val copyleftLimitedLicenses = getLicensesForCategory("copyleft-limited")
val freeRestrictedLicenses = getLicensesForCategory("free-restricted")
val genericLicenses = getLicensesForCategory("generic")
val patentLicenses = getLicensesForCategory("patent-license")
val permissiveLicenses = getLicensesForCategory("permissive")
val proprietaryFreeLicenses = getLicensesForCategory("proprietary-free")
val publicDomainLicenses = getLicensesForCategory("public-domain")
val unknownLicenses = getLicensesForCategory("unknown")
val unstatedLicenses = getLicensesForCategory("unstated-license")

// Set of licenses, which are not acted upon by the below policy rules.
val ignoredLicenses = listOf(
    /**
     * 'generic' category:
     */
    // Contributor License agreement are not relevant for the "use" of open source.
    "LicenseRef-scancode-generic-cla",
    // Permissive licenses are not flagged anyway.
    "LicenseRef-scancode-other-permissive",
    // Public domain licenses are not flagged anyway.
    "LicenseRef-scancode-public-domain",
    // Disclaimers are not relevant because they have no obligations.
    "LicenseRef-scancode-public-domain-disclaimer",
    // Public domain licenses are not flagged anyway.
    "LicenseRef-scancode-us-govt-public-domain",
    // Disclaimers are not relevant because they have no obligations.
    "LicenseRef-scancode-warranty-disclaimer",
    /**
     * 'unknown' category:
     */
    "LicenseRef-scancode-license-file-reference",
    // References to files do not matter, because the target files are also scanned.
    "LicenseRef-scancode-see-license",
    // References to files do not matter, because the target files are also scanned.
    "LicenseRef-scancode-unknown-license-reference"
).map { SpdxSingleLicenseExpression.parse(it) }.toSet()

/**
 * The complete set of licenses covered by policy rules.
 *
 * // TODO: Update the handled licenses to cover all recently added categories. This requires adding
 *          policy rules for new (offinding) categories, if any.
 */
val handledLicenses = listOf(
    commercialLicenses,
    contributorLicenseAgreementLicenenses,
    copyleftLicenses,
    copyleftLimitedLicenses,
    freeRestrictedLicenses,
    genericLicenses,
    patentLicenses,
    permissiveLicenses,
    proprietaryFreeLicenses,
    publicDomainLicenses,
    unknownLicenses,
    unstatedLicenses
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
val orgOssProjectsApprovedLicenses = listOf(
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
        ortResult.hasLabel("project", "oss-project") -> PolicyRules.OSS_PROJECT
        else -> PolicyRules.PROPRIETARY_PROJECT
    }

val enablePriorToOssRules = ortResult.hasLabel("enable-prior-to-oss-rules")

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
fun isApprovedOrgOssProjectLicense(license: SpdxSingleLicenseExpression) = license in orgOssProjectsApprovedLicenses

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
    licenseSource: LicenseSource
): String {
    if (ortResult.isProject(pkg.metadata.id)) {
        // Violation is flagged for the project scanned.
        if (licenseSource == LicenseSource.DETECTED) {
            // License is detected by the scanner in the source code of the project.
            return "${resolveViolationInSourceCodeText(pkg.metadata, license)}".trimMargin()
        }

        // License is declared in project's package manifest file (pom, package.json, etc.).
        return "For this violation, there is no recommended solution.".trimMargin()
    }

    // Violation is thrown for one of the project's dependencies.
    if (licenseSource == LicenseSource.DETECTED) {
        // Violation thrown for license detected by the scanner in the source code of the dependency.
        return "${resolveViolationInDependencySourceCodeText(pkg.metadata, license)}".trimMargin()
    }

    // Violation thrown for declared license in dependency's package manifest file (pom, package.json, etc.).
    return "${resolveViolationInDependencyDeclaredLicenseText(pkg.metadata)}".trimMargin()
}

fun PackageRule.howToFixUnhandledLicense(
    license: String,
    licenseSource: LicenseSource
) : String {
    val createIssueText = """
        |1. If an issue to add this license does not already exist in $orgScanIssueTrackerMdLink, please create it.
        |2. Set the _Summary_ field to 'Add new license $license'.
        |3. Set the _Component/s_ field to _licenses_.
        |4. Set the _Description_ field to something like 'Please add this license to the review tooling.'
        |"""

    if (ortResult.isProject(pkg.metadata.id)) {
        // Unhandled license is found in the project under review.
        if (licenseSource == LicenseSource.DETECTED) {
            // Unhandled license is detected by the scanner in the source code of the project.
            return """
                |${resolveViolationInSourceCodeText(pkg.metadata, license)}
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
                |${resolveViolationInDependencySourceCodeText(pkg.metadata, license)}
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

fun PackageRule.howToFixUnmappedDeclaredLicense(license: String): String {
    val genericDeclaredLicenses = setOf(
        "BSD License",
        "The BSD License"
    )

    return if (license in genericDeclaredLicenses) {
        val binaryUrlMdLink = getArtifactMdLink(pkg.metadata.binaryArtifact.url)
        val vcsUrlMdLink = getVcsMdLink(pkg.metadata)

        """
            |Try to resolve this violation by following the advice below:
            |
            |1. Clone $ortConfigVcsMdLink using Git.
            |2. Map declared license '$license' to an [SPDX license expression](https://spdx.github.io/spdx-spec/appendix-IV-SPDX-license-expressions/):
            |   - Open or create using a text editor `${getPackageCurationsFilePath(pkg.metadata.id)}`.
            |   - Determine the declared licenses for $binaryUrlMdLink by looking for the main license files in the $vcsUrlMdLink.
            |     Use the the following template, changing the text in square brackets (`[...]`) as appropriate.
            |
            |   ```
            |   - id: "${pkg.metadata.id.toCoordinatesWithoutVersion()}"
            |     curations:
            |       comment: "Mapping declared license based on \
            |         [https://url-to-repository/tag-or-revision-for-version-${pkg.metadata.id.version}/LICENSE] and \
            |         [https://url-to-repository/tag-or-revision-for-version-${pkg.metadata.id.version}/package-metadata-file]."
            |       declared_license_mapping:
            |         "$license": "[SPDX license expression for the declared license.]"
            |   ```
            |
            |   - Submit the above change to the $ortConfigVcsMdLink (see $ortConfigContributingMdLink for guidance) with a commit message as shown below.
            |     Reviewers are set automatically.
            |
            |   ```
            |   curations: Map declared license for ${pkg.metadata.id.toCoordinatesWithoutVersion()}
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
        "Maven" -> getArtifactMavenSourcesMdLink(pkg)
        "PIP", "PyPI" -> getArtifactMdLink(pkg.sourceArtifact.url)
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
        "Maven" -> getArtifactMavenSourcesMdLink(pkg)
        "PIP", "PyPI" -> getArtifactMdLink(pkg.sourceArtifact.url)
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
 * Set of matchers to help keep policy rules easy to understand and corresponding helper functions.
 */

fun isException(license: SpdxSingleLicenseExpression): Boolean =
    ("-exception" in license.toString() && " WITH " !in license.toString())

fun PackageRule.hasDefinitionFileName(vararg definitionFileNames: String) =
    object : RuleMatcher {
        private val matchingNames = definitionFileNames.toSet()

        override val description = "hasDefinitionFileName(${matchingNames.joinToString()})"

        override fun matches(): Boolean {
            val project = ortResult.getProject(pkg.metadata.id)
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

        override fun matches() = license in handledLicenses && !isException(license)
    }

fun PackageRule.LicenseRule.isCommercial() =
    object : RuleMatcher {
        override val description = "isCommercial($license)"

        override fun matches() = license in commercialLicenses
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

fun PackageRule.LicenseRule.isException() =
    object : RuleMatcher {
        override val description = "isException($license)"

        override fun matches() = isException(license)
    }

fun PackageRule.LicenseRule.isFreeRestricted() =
    object : RuleMatcher {
        override val description = "isFreeRestricted($license)"

        override fun matches() = license in freeRestrictedLicenses
    }

fun PackageRule.LicenseRule.isGeneric() =
    object : RuleMatcher {
        override val description = "isGeneric($license)"

        override fun matches() = license in genericLicenses
    }

fun PackageRule.LicenseRule.isIgnored() =
    object : RuleMatcher {
        override val description = "isIgnored($license)"

        override fun matches() = license in ignoredLicenses
    }

fun PackageRule.LicenseRule.isProprietaryFree() =
    object : RuleMatcher {
        override val description = "isProprietaryFree($license)"

        override fun matches() = license in proprietaryFreeLicenses
    }

fun PackageRule.LicenseRule.isPatent() =
    object : RuleMatcher {
        override val description = "isPatent($license)"

        override fun matches() = license in patentLicenses
    }

fun PackageRule.LicenseRule.isUnknown() =
    object : RuleMatcher {
        override val description = "isUnknown($license)"

        override fun matches() = license in unknownLicenses
    }

fun PackageRule.LicenseRule.isUnstated() =
    object : RuleMatcher {
        override val description = "isUnstated($license)"

        override fun matches() = license in unstatedLicenses
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
 * Policy rules
 */

fun RuleSet.commercialInDependencyRule() = packageRule("COMMERCIAL_IN_DEPENDENCY") {
    require {
        -isProject()
        -isExcluded()
    }

    licenseRule("COMMERCIAL_IN_DEPENDENCY", LicenseView.CONCLUDED_OR_DECLARED_AND_DETECTED) {
        require {
            +isCommercial()
            -isExcluded()
        }

        error(
            "The dependency '${pkg.metadata.id.toCoordinates()}' is licensed under the ScanCode 'commercial' " +
                    "categorized license $license. This requires approval.",
            howToFixLicenseViolationDefault(license.toString(), licenseSource)
        )
    }
}

fun RuleSet.copyleftInDependencyRule() = dependencyRule("COPYLEFT_IN_DEPENDENCY") {
    require {
        -isProject()
        -isExcluded()
    }

    licenseRule("COPYLEFT_IN_DEPENDENCY", LicenseView.CONCLUDED_OR_DECLARED_AND_DETECTED) {
        require {
            +isCopyleft()
            -isExcluded()
        }


        error(
            "The dependency '${pkg.metadata.id.toCoordinates()}' is licensed under the ScanCode 'copyleft' " +
                    "categorized license $license.",
            howToFixLicenseViolationDefault(license.toString(), licenseSource)
        )
    }
}

fun RuleSet.copyleftLimitedInDependencyRule() = dependencyRule("COPYLEFT_LIMITED_IN_DEPENDENCY") {
    require {
        +isStaticallyLinked()
        -isExcluded()
    }

    licenseRule("COPYLEFT_LIMITED_IN_DEPENDENCY", LicenseView.CONCLUDED_OR_DECLARED_AND_DETECTED) {
        require {
            +isCopyleftLimited()
            -isExcluded()
        }

        error(
            "The dependency '${pkg.metadata.id.toCoordinates()}' is statically linked and licensed under the " +
                    "ScanCode 'copyleft-limited' categorized license $license.",
            howToFixLicenseViolationDefault(license.toString(), licenseSource)
        )
    }
}

fun RuleSet.copyleftInSourceRule() = packageRule("COPYLEFT_IN_SOURCE") {
    require {
        +isProject()
        -isExcluded()
    }

    licenseRule("COPYLEFT_IN_SOURCE", LicenseView.CONCLUDED_OR_DECLARED_AND_DETECTED) {
        require {
            -isExcluded()
            +isCopyleft()
        }

        error(
            "The ScanCode 'copyleft' categorized license $license was ${licenseSource.name.lowercase()} in project " +
                    "${pkg.metadata.id.toCoordinates()}.",
            howToFixLicenseViolationDefault(license.toString(), licenseSource)
        )
    }
}

fun RuleSet.copyleftLimitedInSourceRule() = packageRule("COPYLEFT_LIMITED_IN_SOURCE") {
    require {
        +isProject()
        -isExcluded()
    }

    licenseRule("COPYLEFT_LIMITED_IN_SOURCE", LicenseView.CONCLUDED_OR_DECLARED_AND_DETECTED) {
        require {
            -isExcluded()
            +isCopyleftLimited()
        }

        error(
            "The ScanCode 'copyleft-limited' categorized license $license was ${licenseSource.name.lowercase()} in " +
                    "project ${pkg.metadata.id.toCoordinates()}.",
            howToFixLicenseViolationDefault(license.toString(), licenseSource)
        )
    }
}

fun RuleSet.dependencyInProjectSourceRule() = projectSourceRule("DEPENDENCY_IN_PROJECT_SOURCE_RULE") {
    val denyDirPatterns = listOf(
        "**/node_modules" to setOf("NPM", "Yarn", "PNPM"),
        "**/vendor" to setOf("GoMod", "GoDep")
    )

    denyDirPatterns.forEach { (pattern, packageManagers) ->
        val offendingDirs = projectSourceFindDirectories(pattern)

        if (offendingDirs.isNotEmpty()) {
            error(
                "The directories ${offendingDirs.joinToString()} belong to the package manager(s) " +
                        "${packageManagers.joinToString()} and must not be committed.",
                "Please delete the directories: ${offendingDirs.joinToString()}."
            )
        }
    }
}

fun RuleSet.deprecatedScopeExludeInOrtYmlRule() = ortResultRule("DEPRECATED_SCOPE_EXCLUDE_REASON_IN_ORT_YML") {
    val reasons = ortResult.repository.config.excludes.scopes.mapTo(mutableSetOf()) { it.reason }

    @Suppress("DEPRECATION")
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

fun RuleSet.freeRestrictedInDependencyRule() = packageRule("FREE_RESTRICTED_IN_DEPENDENCY") {
    require {
        -isProject()
        -isExcluded()
    }

    licenseRule("FREE_RESTRICTED_IN_DEPENDENCY", LicenseView.CONCLUDED_OR_DECLARED_AND_DETECTED) {
        require {
            +isFreeRestricted()
            -isExcluded()
        }

        error(
            "The dependency '${pkg.metadata.id.toCoordinates()}' is licensed under the ScanCode 'free-restricted' " +
                    "categorized license $license. This requires approval.",
            howToFixLicenseViolationDefault(license.toString(), licenseSource)
        )
    }
}

fun RuleSet.genericInDependencyRule() = packageRule("GENERIC_IN_DEPENDENCY") {
    require {
        -isProject()
        -isExcluded()
    }

    licenseRule("GENERIC_IN_DEPENDENCY", LicenseView.CONCLUDED_OR_DECLARED_AND_DETECTED) {
        require {
            +isGeneric()
            -isIgnored()
        }

        error(
            "The dependency '${pkg.metadata.id.toCoordinates()}' might contain a license which is unknown to the " +
                    " tooling. It was detected as $license which is just a trigger, but not a real license. Please " +
                    "create a dedicated license identifier if the finding is valid.",
            howToFixLicenseViolationDefault(license.toString(), licenseSource)
        )
    }
}

fun RuleSet.missingCiConfigurationRule() = projectSourceRule("MISSING_CI_CONFIGURATION") {
    require {
        -AnyOf(
            projectSourceHasFile(
                ".appveyor.yml",
                ".bitbucket-pipelines.yml",
                ".gitlab-ci.yml",
                ".travis.yml"
            ),
            projectSourceHasDirectory(
                ".circleci",
                ".github/workflows"
            )
        )
    }

    error(
        message = "This project does not have any known CI configuration files.",
        howToFix = "Please setup a CI. If you already have setup a CI and the error persists, please contact support."
    )
}

fun RuleSet.missingContributingFileRule() = projectSourceRule("MISSING_CONTRIBUTING_FILE") {
    require {
        -projectSourceHasFile("CONTRIBUTING.md")
    }

    error("The project's code repository does not contain the file 'CONTRIBUTING.md'.")
}

fun RuleSet.missingGitignoreFileRule() = projectSourceRule("MISSING_GITIGNORE_FILE") {
    require {
        +projectSourceHasVcsType(VcsType.GIT)
        -projectSourceHasFile(".gitignore")
    }

    error(
        message = "Adding a '.gitignore' file is recommended practice to prevent pushing files with sensitive " +
            "information, compiled code, system files, caches, logs or generated files such as dist directories.",
        howToFix = "A wide variety of gitignore template files for specific programming languages, frameworks, tools " +
            "and environments can be found at https://github.com/github/gitignore."
    )
}

fun RuleSet.missingLicenseFileRule() = projectSourceRule("MISSING_LICENSE_FILE") {
    require {
        -projectSourceHasFile("LICENSE")
    }

    error(
        message = "The project's code repository does not contain the file 'LICENSE'."
    )
}

fun RuleSet.missingReadmeFileRule() = projectSourceRule("MISSING_README_FILE") {
    require {
        -projectSourceHasFile("README.md")
    }

    error("The project's code repository does not contain the file 'README.md'.")
}

fun RuleSet.missingReadmeFileLicenseSectionRule() = projectSourceRule("MISSING_README_FILE_LICENSE_SECTION") {
    require {
        +projectSourceHasFile("README.md")
        -projectSourceHasFileWithContent(".*^#{1,2} License$.*", "README.md")
    }

    error(
        message = "The file 'README.md' is missing a \"License\" section.",
        howToFix = "Please add a \"License\" section to the file 'README.md'."
    )
}

fun RuleSet.missingTestsRule() = projectSourceRule("MISSING_TESTS") {
    require {
        -projectSourceHasDirectory(
            "**/*test*",
            "**/*Test*",
        )
    }

    error(
        message = "This project does not seem to have any tests.",
        howToFix = "Please setup tests. If you already have tests and the error persists, please contact support."
    )
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

fun RuleSet.patentInDependencyRule() = packageRule("PATENT_IN_DEPENDENCY") {
    require {
        -isProject()
        -isExcluded()
    }

    licenseRule("PATENT_IN_DEPENDENCY", LicenseView.CONCLUDED_OR_DECLARED_AND_DETECTED) {
        require {
            +isPatent()
            -isExcluded()
        }

        error(
            "The dependency '${pkg.metadata.id.toCoordinates()}' is licensed under the ScanCode 'patent-license' " +
                    "categorized license $license. This requires approval.",
            howToFixLicenseViolationDefault(license.toString(), licenseSource)
        )
    }
}

fun RuleSet.proprietaryFreeInDependencyRule() = packageRule("PROPRIETARY_FREE_IN_DEPENDENCY") {
    require {
        -isProject()
        -isExcluded()
    }

    licenseRule("PROPRIETARY_FREE_IN_DEPENDENCY", LicenseView.CONCLUDED_OR_DECLARED_AND_DETECTED) {
        require {
            +isProprietaryFree()
            -isExcluded()
        }

        error(
            "The dependency '${pkg.metadata.id.toCoordinates()}' is licensed under the ScanCode 'proprietary-free' " +
                    "categorized license $license. This requires approval.",
            howToFixLicenseViolationDefault(license.toString(), licenseSource)
        )
    }
}

fun RuleSet.unkownInDependencyRule() = packageRule("UNKNOWN_IN_DEPENDENCY") {
    require {
        -isProject()
        -isExcluded()
    }

    licenseRule("UNKNOWN_IN_DEPENDENCY", LicenseView.CONCLUDED_OR_DECLARED_AND_DETECTED) {
        require {
            +isUnknown()
            -isIgnored()
            -isExcluded()
        }

        error(
            "The dependency '${pkg.metadata.id.toCoordinates()}' might contain a license which is unknown to the " +
                    " tooling. It was detected as $license which is just a trigger, but not a real license. Please " +
                    "create a dedicated license identifier if the finding is valid.",
            howToFixLicenseViolationDefault(license.toString(), licenseSource)
        )
    }
}

fun RuleSet.unstatedInDependencyRule() = packageRule("UNSTATED_IN_DEPENDENCY") {
    require {
        -isProject()
        -isExcluded()
    }

    licenseRule("UNSTATED_IN_DEPENDENCY", LicenseView.CONCLUDED_OR_DECLARED_AND_DETECTED) {
        require {
            +isUnstated()
            -isExcluded()
        }

        error(
            "The dependency '${pkg.metadata.id.toCoordinates()}' is licensed under the ScanCode 'unstated-licenses' " +
                    "categorized license $license. This requires approval.",
            howToFixLicenseViolationDefault(license.toString(), licenseSource)
        )
    }
}

fun RuleSet.vulnerabilityInDependencyRule() = packageRule("VULNERABILITY_IN_DEPENDENCY") {
    require {
        -isProject()
        -isExcluded()
        +hasVulnerability()
    }

    warning(
        "The package '${pkg.metadata.id.toCoordinates()}' has a vulnerability",
        howToFixDefault()
    )
}

fun RuleSet.vulnerabilityWithHighSeverityInDependencyRule() = packageRule("HIGH_SEVERITY_VULNERABILITY_IN_DEPENDENCY") {
    val maxAcceptedSeverity = "5.0"
    val scoringSystem = "CVSS2"

    require {
        -isProject()
        -isExcluded()
        +hasVulnerability(maxAcceptedSeverity, scoringSystem) { value, threshold ->
            value.toFloat() >= threshold.toFloat()
        }
    }

    error(
        "The package '${pkg.metadata.id.toCoordinates()}' has a vulnerability with $scoringSystem severity > " +
                "$maxAcceptedSeverity",
        howToFixDefault()
    )
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
            "Package '${pkg.metadata.id.toCoordinates()}' declares $license which is not an " +
                    "approved license within $orgName.",
            howToFixOssProjectDefault()
        )
    }
}

fun RuleSet.unhandledLicenseRule() = packageRule("UNHANDLED_LICENSE") {
    require {
        -isExcluded()
    }

    licenseRule("UNHANDLED_LICENSE", LicenseView.CONCLUDED_OR_DECLARED_AND_DETECTED) {
        require {
            -isExcluded()
            -isHandled()
            -isException()
        }

        error(
            "The license $license is currently not covered by policy rules. " +
                    "The license was ${licenseSource.name.lowercase()} in package " +
                    "${pkg.metadata.id.toCoordinates()}",
            howToFixUnhandledLicense(license.toString(), licenseSource)
        )
    }
}

fun RuleSet.unmappedDeclaredLicenseRule() = packageRule("UNMAPPED_DECLARED_LICENSE") {
    require {
        -isExcluded()
    }

    resolvedLicenseInfo.licenseInfo.declaredLicenseInfo.processed.unmapped.forEach { unmappedLicense ->
        warning(
            "The declared license '$unmappedLicense' could not be mapped to a valid license or parsed as an SPDX " +
                    "expression. The license was found in package ${pkg.metadata.id.toCoordinates()}.",
            howToFixUnmappedDeclaredLicense(unmappedLicense)
        )
    }
}

fun RuleSet.wrongLicenseInLicenseFileRule() = projectSourceRule("WRONG_LICENSE_IN_LICENSE_FILE_RULE") {
    require {
        +projectSourceHasFile("LICENSE")
    }

    val allowedRootLicenses = orgOssProjectsApprovedLicenses.mapTo(mutableSetOf()) { it.simpleLicense() }
    val detectedRootLicenses = projectSourceGetDetectedLicensesByFilePath("LICENSE").values.flatten().toSet()
    val wrongLicenses = detectedRootLicenses - allowedRootLicenses

    if (wrongLicenses.isNotEmpty()) {
        error(
            message = "The file 'LICENSE' contains the following disallowed licenses ${wrongLicenses.joinToString()}.",
            howToFix = "Please use only the following allowed licenses: ${allowedRootLicenses.joinToString()}."
        )
    } else if (detectedRootLicenses.isEmpty()) {
        error(
            message = "The file 'LICENSE' does not contain any license which is not allowed.",
            howToFix = "Please use one of the following allowed licenses: ${allowedRootLicenses.joinToString()}."
        )
    }
}

fun RuleSet.commonRules() {
    unhandledLicenseRule()
    unmappedDeclaredLicenseRule()

    // Rules applicable to the `.ort.yml` file:
    deprecatedScopeExludeInOrtYmlRule()
    packageConfigurationInOrtYmlRule()
    packageCurationInOrtYmlRule()

    // Rules for dependencies:
    vulnerabilityInDependencyRule()
    vulnerabilityWithHighSeverityInDependencyRule()

    // Prior to open sourcing use case rules (which get executed once):
    if (enablePriorToOssRules) {
        dependencyInProjectSourceRule()
        missingCiConfigurationRule()
        missingContributingFileRule()
        missingGitignoreFileRule()
        missingLicenseFileRule()
        missingReadmeFileRule()
        missingReadmeFileLicenseSectionRule()
        missingTestsRule()
        wrongLicenseInLicenseFileRule()
    }
}

fun RuleSet.ossProjectRules() {
    // Rules for project sources:
    unapprovedOssProjectLicenseRule()
}

fun RuleSet.proprietaryProjectRules() {
    // Rules for project sources:
    copyleftInSourceRule()
    copyleftLimitedInSourceRule()

    // Rules for dependencies:
    commercialInDependencyRule()
    copyleftInDependencyRule()
    copyleftLimitedInDependencyRule()
    freeRestrictedInDependencyRule()
    genericInDependencyRule()
    patentInDependencyRule()
    proprietaryFreeInDependencyRule()
    unkownInDependencyRule()
    unstatedInDependencyRule()
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
