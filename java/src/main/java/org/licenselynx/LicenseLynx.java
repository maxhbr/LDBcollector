/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: Apache-2.0
 */
package org.licenselynx;

import javax.annotation.CheckForNull;

import javax.annotation.Nonnull;


/**
 * LicenseLynx class to map license names to their corresponding data from a JSON file.
 */
public final class LicenseLynx
{

    // Private constructor to prevent instantiation
    private LicenseLynx()
    {
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
        LicenseMapSingleton licenseMapSingleton = LicenseMapSingleton.getInstance();
        LicenseMap licenseMap = licenseMapSingleton.getLicenseMap();

        return licenseMap.getCanonicalLicenseMap().get(pLicenseName);
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
        LicenseMapSingleton licenseMapSingleton = LicenseMapSingleton.getInstance();
        LicenseMap licenseMap = licenseMapSingleton.getLicenseMap();

        LicenseObject licenseObject = licenseMap.getCanonicalLicenseMap().get(pLicenseName);

        if (licenseObject == null && pRisky) {
            licenseObject = licenseMap.getRiskyLicenseMap().get(pLicenseName);
        }

        return licenseObject;
    }
}

