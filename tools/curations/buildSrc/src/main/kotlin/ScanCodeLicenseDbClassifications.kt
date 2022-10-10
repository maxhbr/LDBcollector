package org.ossreviewtoolkit.tools.curations

import com.fasterxml.jackson.databind.PropertyNamingStrategies
import com.fasterxml.jackson.databind.json.JsonMapper
import com.fasterxml.jackson.module.kotlin.KotlinFeature
import com.fasterxml.jackson.module.kotlin.KotlinModule
import com.fasterxml.jackson.module.kotlin.readValue

import java.net.URL
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentLinkedQueue

import kotlin.time.measureTime

import org.gradle.api.logging.Logging
import org.ossreviewtoolkit.model.licenses.LicenseCategorization
import org.ossreviewtoolkit.model.licenses.LicenseCategory
import org.ossreviewtoolkit.model.licenses.LicenseClassifications
import org.ossreviewtoolkit.model.yamlMapper
import org.ossreviewtoolkit.utils.spdx.SpdxSingleLicenseExpression

private val INDEX_JSON_URL =  "https://scancode-licensedb.aboutcode.org/index.json"
private val DISCLAIMER_TEXT = """
License classification generated based on https://scancode-licensedb.aboutcode.org/.    
    
This ORT configuration file is provided as an example only. It
demonstrates the general configuration capabilities of ORT and does not
reflect any real-world configuration used by the ORT contributors, nor
are they a recommendation on the configuration to use.

Please consult your legal counsel about how ORT should be configured for your use cases.

For detailed documentation on this file, see
https://github.com/oss-review-toolkit/ort/blob/main/docs/config-file-license-classifications-yml.md.
"""

private val LOGGER = Logging.getLogger("ScanCodeLicenseDbClassifications")
private val JSON_MAPPER = JsonMapper().apply {
    KotlinModule.Builder()
        .configure(KotlinFeature.NullIsSameAsDefault, true)
        .build()
        .let { registerModule(it) }

    propertyNamingStrategy = PropertyNamingStrategies.SNAKE_CASE
}

private data class License(
    val licenseKey: String,
    val spdxLicenseKey: String? = null,
    val otherSpdxLicenseKeys: List<String> = emptyList(),
    val isException: Boolean,
    val isDeprecated: Boolean,
    val category: String,
    val json: String,
    val yml: String,
    val html: String,
    val text: String
)

private data class LicenseDetails(
    val key: String,
    val shortName: String,
    val name: String,
    val category: String,
    val owner: String,
    val homepageUrl: String? = null,
    val notes: String? = null,
    val spdxLicenseKey: String? = null,
    val minimumCoverage: Int? = null,
    val standardNotice: String? = null,
    val isDeprecated: Boolean = false,
    val isException: Boolean = false,
    val isGeneric: Boolean = false,
    val isUnknown: Boolean = false,
    val ignorableCopyrights: List<String> = emptyList(),
    val ignorableHolders: List<String> = emptyList(),
    val ignorableAuthors: List<String> = emptyList(),
    val ignorableEmails: List<String> = emptyList(),
    val ignorableUrls: List<String> = emptyList(),
    val textUrls: List<String> = emptyList(),
    val otherUrls: List<String> = emptyList(),
    val faqUrl: String? = null,
    val osiLicenseKey: String? = null,
    val otherSpdxLicenseKeys: List<String> = emptyList(),
    val osiUrl: String? = null,
    val language: String? = null
)

private fun downloadLicenseIndex(): List<License> =
    JSON_MAPPER.readValue<List<License>>(URL(INDEX_JSON_URL))

private fun downloadLicenseDetails(license: License): LicenseDetails {
    val url = INDEX_JSON_URL.substringBeforeLast("/") + "/${license.json}"
    LOGGER.info("GET $url.")
    return JSON_MAPPER.readValue<LicenseDetails>(URL(url))
}

@OptIn(kotlin.time.ExperimentalTime::class)
private fun downloadLicenseDetailsBatched(
    licenses: Collection<License>,
    threadCount: Int = 60
): Map<License, LicenseDetails> {
    val queue = ConcurrentLinkedQueue(licenses)
    val result = ConcurrentHashMap<License, LicenseDetails>()

    val threads = List(threadCount) { _ ->
        Thread {
            var license = queue.poll()

            while (license != null) {
                result[license] = downloadLicenseDetails(license)
                license = queue.poll()
            }
        }
    }

    val executionTime = measureTime {
        threads.run {
            forEach { it.start() }
            forEach { it.join() }
        }
    }

    LOGGER.quiet("Downloaded ${result.size} files in $executionTime on $threadCount threads.")

    return result.toMap()
}

private fun LicenseDetails.getLicenseId(): SpdxSingleLicenseExpression {
    val expression = spdxLicenseKey ?: otherSpdxLicenseKeys.firstOrNull() ?: "LicenseRef-scancode-${key}"
    return SpdxSingleLicenseExpression.parse(expression)
}

private fun LicenseDetails.getCategories(): Set<String> {
    // TODO: Check if the category "Unstated License" could additionally be used by below mapping to move
    // license IDs which do not correspond to a "normal" license to separate categories.
    val mappedCategory = when {
        isUnknown -> "unknown"
        isGeneric -> "generic"
        else -> category.replace(' ', '-').toLowerCase()
    }

    return setOfNotNull(
        mappedCategory,
        // Include all licenses into the notice file to ensure there is no under-reporting by default.
        "include-in-notice-file",
        // The FSF has stated that a source code offer is required for Copyleft (limited) licences, so
        // include only these to not cause unnecessary effort by default.
        "include-source-code-offer-in-notice-file".takeIf { mappedCategory in setOf("copyleft", "copyleft-limited") }
    )
}

private fun getLicenseClassifications(licenseDetails: Collection<LicenseDetails>) =
    LicenseClassifications(
        categories = licenseDetails.flatMap { it.getCategories() }.distinct().map {
            LicenseCategory(it)
        }.sortedBy { it.name },
        categorizations = licenseDetails.map {
            LicenseCategorization(
                id = it.getLicenseId(),
                categories = it.getCategories()
            )
        }.sortedBy { it.id.toString() }
    )

/**
 * Generate license classifications from ScanCode's license categories.
 *
 * The original categories are used except for 'unknown' and 'generic' licenses, which are assigned to a separate
 * category.
 */
fun generateLicenseClassificationsYaml(): String {
    val licenses = downloadLicenseIndex().filterNot {
        it.isException || it.licenseKey == "x11-xconsortium_veillard"
    }
    val licenseDetails = downloadLicenseDetailsBatched(licenses).values
    val licenseClassifications = getLicenseClassifications(licenseDetails)

    licenseClassifications.run {
        LOGGER.quiet(
            "Generated a license classification with ${categorizations.size} license and ${categories.size} categories."
        )
    }

    val yaml = yamlMapper.writerWithDefaultPrettyPrinter().writeValueAsString(licenseClassifications)
    val disclaimer = DISCLAIMER_TEXT.split('\n').map { "# $it".trim() }.joinToString("\n")

    return "$disclaimer\n$yaml"
}
