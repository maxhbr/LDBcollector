
/*
SPDX-FileCopyrightText: 2021 HH Partners, Attorneys-at-law Ltd <doubleopen@hhpartners.fi>
SPDX-License-Identifier: CC0-1.0
*/

val permissiveLicenses = licenseClassifications.licensesByCategory["permissive"].orEmpty()
val copyleftLicenses = licenseClassifications.licensesByCategory["copyleft"].orEmpty()

// The complete set of licenses covered by policy rules.
val handledLicenses = listOf(
    permissiveLicenses,
).flatten().let {
    it.toSet()
}

fun PackageRule.LicenseRule.isHandled() =
    object : RuleMatcher {
        override val description = "isHandled($license)"

        override fun matches() = license in handledLicenses
    }

// Define the set of policy rules.
val ruleSet = ruleSet(ortResult, licenseInfoResolver) {}

// Populate the list of policy rule violations to return.
ruleViolations += ruleSet.violations
