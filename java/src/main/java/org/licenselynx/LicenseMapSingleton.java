package com.siemens.licenselynx;

import com.siemens.licenselynx.dto.LicenseMap;


class LicenseMapSingleton
{
    private final LicenseMap licenseMap;

    private static LicenseMapSingleton instance;



    private LicenseMapSingleton()
    {
        if (instance != null)
        {
            throw new InstantiationError();
        }

        this.licenseMap = new LicenseDataLoader().loadLicenses();
    }




    public static synchronized LicenseMapSingleton getInstance()
    {
        if (instance == null)
        {
            instance = new LicenseMapSingleton();
        }
        return instance;
    }



    public LicenseMap getLicenseMap()
    {
        return licenseMap;
    }
}
