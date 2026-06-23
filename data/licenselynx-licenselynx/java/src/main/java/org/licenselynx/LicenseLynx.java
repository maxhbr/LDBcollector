/*
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import javax.annotation.CheckForNull;
import javax.annotation.Nonnull;


/**
 * LicenseLynx class to map license names to their corresponding data from a JSON file.
 */
public final class LicenseLynx
{
    private LicenseLynx()
    {
        // Private constructor to prevent instantiation
    }



    /**
     * Maps the given license name to its corresponding LicenseObject.
     *
     * @param pLicenseName the name of the license to map
     * @return the license data as a LicenseObject, or null if not found
     */
    @CheckForNull
    public static LicenseObject map(@Nonnull final String pLicenseName)
    {
        return map(pLicenseName, false, null, getLicenseMap());
    }



    /**
     * Maps the given license name to its corresponding LicenseObject.
     * It also searches through the risky license mappings, when the boolean value is set.
     *
     * @param pLicenseName the name of the license to map
     * @param pRisky boolean flag to enable risky mappings
     * @return the license data as a LicenseObject, or null if not found
     */
    @CheckForNull
    public static LicenseObject map(@Nonnull final String pLicenseName, final boolean pRisky)
    {
        return map(pLicenseName, pRisky, null, getLicenseMap());
    }



    /**
     * Maps the given license name to its corresponding LicenseObject.
     * Searches through stable mappings and an organization-specific mapping.
     *
     * @param pLicenseName the name of the license to map
     * @param pOrganization the organization to search in
     * @return the license data as a LicenseObject, or null if not found
     */
    @CheckForNull
    public static LicenseObject map(@Nonnull final String pLicenseName, @Nonnull final Organization pOrganization)
    {
        return map(pLicenseName, false, pOrganization, getLicenseMap());
    }



    /**
     * Maps the given license name to its corresponding LicenseObject.
     * Searches through stable mappings, optionally risky mappings, and optionally
     * an organization-specific mapping.
     *
     * @param pLicenseName the name of the license to map
     * @param pRisky boolean flag to enable risky mappings
     * @param pOrganization the organization to search in, or null to skip org lookup
     * @return the license data as a LicenseObject, or null if not found
     */
    @CheckForNull
    public static LicenseObject map(@Nonnull final String pLicenseName, final boolean pRisky,
        @CheckForNull final Organization pOrganization)
    {
        return map(pLicenseName, pRisky, pOrganization, getLicenseMap());
    }



    @CheckForNull
    static LicenseObject map(@Nonnull final String pLicenseName, final boolean pRisky,
        @CheckForNull final Organization pOrganization, @Nonnull final LicenseMap pLicenseMap)
    {
        String licenseNameNormalized = QuotesHandler.normalizeQuotes(pLicenseName);
        LicenseObject licenseObject = pLicenseMap.getCanonicalLicenseMap().get(licenseNameNormalized);

        if (licenseObject == null && pRisky) {
            licenseObject = pLicenseMap.getRiskyLicenseMap().get(licenseNameNormalized);
        }

        if (licenseObject == null && pOrganization != null) {
            licenseObject = pLicenseMap.getOrganizationMap(pOrganization).get(licenseNameNormalized);
        }

        return licenseObject;
    }



    @Nonnull
    private static LicenseMap getLicenseMap()
    {
        return new LicenseMap();
    }
}
