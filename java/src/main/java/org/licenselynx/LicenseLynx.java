package com.siemens.licenselynx;

import com.siemens.licenselynx.dto.LicenseMap;
import com.siemens.licenselynx.dto.LicenseObject;

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
    public static LicenseObject map(final String pLicenseName)
    {
        LicenseMapSingleton licenseMapSingleton = LicenseMapSingleton.getInstance();
        LicenseMap licenseMap = licenseMapSingleton.getLicenseMap();

        return licenseMap.getLicenseObject(pLicenseName);
    }
}
