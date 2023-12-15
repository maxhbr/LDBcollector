#!/usr/bin/env kotlin

// SPDX-FileCopyrightText: 2023 Double Open Oy <support@doubleopen.org>
// SPDX-License-Identifier: CC0-1.0

@file:CompilerOptions("-jvm-target", "17")
@file:DependsOn("org.ossreviewtoolkit:model:10.0.0")

import java.io.File

import kotlin.system.exitProcess

import org.ossreviewtoolkit.model.licenses.LicenseClassifications
import org.ossreviewtoolkit.model.readValue

val scriptsDir = __FILE__.parentFile
val licenseClassificationsFile = scriptsDir.resolve("../license-classifications.yml").canonicalFile

val licenseClassifications = runCatching {
    licenseClassificationsFile.readValue<LicenseClassifications>()
}.onFailure {
    println("Unable to read '$licenseClassificationsFile': ${it.message}")
}.getOrElse {
    exitProcess(1)
}

println("Check passed for '$licenseClassificationsFile'.")
