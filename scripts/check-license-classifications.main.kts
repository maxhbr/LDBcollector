#!/usr/bin/env kotlin

// SPDX-FileCopyrightText: 2023 Double Open Oy <support@doubleopen.org>
// SPDX-License-Identifier: CC0-1.0

@file:CompilerOptions("-jvm-target", "11")
@file:DependsOn("org.ossreviewtoolkit:model:18.0.0")

import kotlin.system.exitProcess

import org.ossreviewtoolkit.model.licenses.LicenseClassifications
import org.ossreviewtoolkit.model.readValue
import org.ossreviewtoolkit.utils.spdx.SpdxExpression.Strictness

val scriptsDir = __FILE__.parentFile
val licenseClassificationsFile = scriptsDir.resolve("../license-classifications.yml").canonicalFile

val licenseClassifications = runCatching {
    licenseClassificationsFile.readValue<LicenseClassifications>()
}.onFailure {
    println("Unable to read '$licenseClassificationsFile': ${it.message}")
}.getOrElse {
    exitProcess(1)
}

val (validLicenses, invalidLicenses) = licenseClassifications.categoriesByLicense.keys.partition {
    it.isValid(Strictness.ALLOW_ANY)
}

if (invalidLicenses.isNotEmpty()) {
    println("The following licenses cannot be parsed as SPDX license expressions:")
    println(invalidLicenses.joinToString("\n"))
    exitProcess(1)
}

println("Check passed for '$licenseClassificationsFile'.")
