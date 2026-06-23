/*
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;


/**
 * Smoke tests that check the end user API.
 */
public class SmokeTest
{
    @Test
    public void stableMapLookup()
    {
        LicenseObject result = LicenseLynx.map("0BSD");
        Assertions.assertNotNull(result, "Expected a result for '0BSD'");
        Assertions.assertEquals("0BSD", result.getId());
        Assertions.assertEquals(LicenseSource.Spdx, result.getCanonicalSource());
    }



    @Test
    public void riskyMapLookupWithFlag()
    {
        LicenseObject result = LicenseLynx.map("LIbpng License v2", true);
        Assertions.assertNotNull(result, "Expected a result for 'LIbpng License v2' with risky=true");
        Assertions.assertEquals("libpng-2.0", result.getId());
    }



    @Test
    public void riskyEntryNotResolvedWithoutFlag()
    {
        LicenseObject result = LicenseLynx.map("LIbpng License v2");
        Assertions.assertNull(result, "Expected null for 'LIbpng License v2' without risky=true");
    }



    @Test
    public void organizationScopedLookup()
    {
        LicenseObject result = LicenseLynx.map("Siemens Inner Source License v1.5", Organization.Siemens);
        Assertions.assertNotNull(result, "Expected a result for Organization.Siemens");
        Assertions.assertEquals("SISL-1.5", result.getId());
        Assertions.assertEquals("siemens", result.getCanonicalSource().getValue());
    }



    @Test
    public void riskyOrganizationScopedLookup()
    {
        LicenseObject result = LicenseLynx.map("Siemens Inner Source License v1.5", true, Organization.Siemens);
        Assertions.assertNotNull(result, "Expected a result for Organization.Siemens");
        Assertions.assertEquals("SISL-1.5", result.getId());
        Assertions.assertEquals("siemens", result.getCanonicalSource().getValue());
    }



    @Test
    public void organizationEntryNotResolvedWithoutOrg()
    {
        LicenseObject result = LicenseLynx.map("Siemens Inner Source License v1.5");
        Assertions.assertNull(result, "Expected null without org parameter");
    }
}
