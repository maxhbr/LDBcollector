/*
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;


/**
 * Holder of all the organization-specific mappings.
 */
public final class CustomOrgMap
{
    private static final Map<Organization, Map<String, LicenseObject>> VALUES;

    static {
        Map<Organization, Map<String, LicenseObject>> m = new HashMap<>();

        // Add lines here if new organizations are added. CodeGeneratorTask replaces "Xxx" with the org enum value key.
        m.put(Organization.Siemens, CustomOrgXxxMap.getLicenseMap());

        VALUES = Collections.unmodifiableMap(m);
    }



    private CustomOrgMap()
    {
        // static class, do not instantiate
    }



    public static Map<Organization, Map<String, LicenseObject>> getOrgMaps()
    {
        return VALUES;
    }
}
