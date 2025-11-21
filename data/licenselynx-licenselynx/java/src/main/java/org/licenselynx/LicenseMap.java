/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import net.jcip.annotations.Immutable;

import javax.annotation.Nonnull;
import java.util.Map;
import java.util.Objects;


/**
 * LicenseMap represents the two JSON Objects for the canonical license map and the risky license map
 * It provides getters to access these properties.
 */
@Immutable
class LicenseMap
{
    @JsonProperty
    private final Map<String, LicenseObject> canonicalLicenseMap;

    @JsonProperty
    private final Map<String, LicenseObject> riskyLicenseMap;



    @JsonCreator
    public LicenseMap(
        @JsonProperty("stableMap") final Map<String, LicenseObject> pCanonicalLicenseMap,
        @JsonProperty("riskyMap") final Map<String, LicenseObject> pRiskyLicenseMap)
    {
        this.canonicalLicenseMap = Objects.requireNonNull(pCanonicalLicenseMap);
        this.riskyLicenseMap = Objects.requireNonNull(pRiskyLicenseMap);
    }



    /**
     * Gets the canonical license map.
     * @return canonical license map
     */
    @Nonnull
    public Map<String, LicenseObject> getCanonicalLicenseMap()
    {
        return canonicalLicenseMap;
    }



    /**
     * Gets the risky license map.
     * @return risky license map
     */
    @Nonnull
    public Map<String, LicenseObject> getRiskyLicenseMap()
    {
        return riskyLicenseMap;
    }
}
