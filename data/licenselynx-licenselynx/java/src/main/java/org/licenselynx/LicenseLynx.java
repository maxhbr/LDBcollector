/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: Apache-2.0
 */
package org.licenselynx;

import javax.annotation.CheckForNull;

import javax.annotation.Nonnull;

import java.util.Map;


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
        Map<String, LicenseObject> licenseMap = licenseMapSingleton.getLicenseMap();

        return licenseMap.get(pLicenseName);
    }
}
