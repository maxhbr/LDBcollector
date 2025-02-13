package com.siemens.licenselynx;

import com.siemens.licenselynx.dto.LicenseMap;

/**
 * Interface for loading license data.
 */
public interface LicenseDataProvider {
    LicenseMap loadLicenses();
}
