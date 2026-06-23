/*
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import java.util.Collections;
import java.util.Map;
import javax.annotation.Nonnull;

import net.jcip.annotations.Immutable;


/**
 * LicenseMap represents the JSON structure containing the canonical license map,
 * the risky license map, and organization-specific license maps.
 * It provides getters to access these properties.
 */
@Immutable
class LicenseMap
{
    private final Map<String, LicenseObject> canonicalLicenseMap;

    private final Map<String, LicenseObject> riskyLicenseMap;

    private final Map<Organization, Map<String, LicenseObject>> organizationMaps;



    LicenseMap()
    {
        this(StableMap.getLicenseMap(), RiskyMap.getLicenseMap(), CustomOrgMap.getOrgMaps());
    }



    LicenseMap(@Nonnull final Map<String, LicenseObject> pStableMap,
        @Nonnull final Map<String, LicenseObject> pRiskyMap,
        @Nonnull final Map<Organization, Map<String, LicenseObject>> pOrgMaps)
    {
        super();
        canonicalLicenseMap = pStableMap;
        riskyLicenseMap = pRiskyMap;
        organizationMaps = pOrgMaps;
    }



    /**
     * Gets the canonical license map.
     *
     * @return canonical license map
     */
    @Nonnull
    Map<String, LicenseObject> getCanonicalLicenseMap()
    {
        return canonicalLicenseMap;
    }



    /**
     * Gets the risky license map.
     *
     * @return risky license map
     */
    @Nonnull
    Map<String, LicenseObject> getRiskyLicenseMap()
    {
        return riskyLicenseMap;
    }



    /**
     * Gets the license map for a specific organization.
     *
     * @param pOrganization the organization to look up
     * @return the organization's license map, or an empty map if the organization has no entries
     */
    @Nonnull
    Map<String, LicenseObject> getOrganizationMap(@Nonnull final Organization pOrganization)
    {
        return organizationMaps.getOrDefault(pOrganization, Collections.emptyMap());
    }



    /**
     * Gets all organization license maps.
     *
     * @return unmodifiable map of organization to their license maps
     */
    @Nonnull
    Map<Organization, Map<String, LicenseObject>> getOrganizationMaps()
    {
        return Collections.unmodifiableMap(organizationMaps);
    }
}
