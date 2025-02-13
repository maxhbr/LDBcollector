package com.siemens.licenselynx.dto;

import java.util.Map;


public class LicenseMap
{
    private final Map<String, LicenseObject> mergedLicenseMap;

    public LicenseMap(Map<String, LicenseObject> mergedLicenseMap) {
        this.mergedLicenseMap = mergedLicenseMap;
    }



    public Map<String, LicenseObject> getMergedLicenseMap()
    {
        return mergedLicenseMap;
    }

    public LicenseObject getLicenseObject(String pLicenseName)
    {
        return this.mergedLicenseMap.get(pLicenseName);
    }
}
