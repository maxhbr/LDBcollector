/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: Apache-2.0
 */
package org.licenselynx;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

import net.jcip.annotations.Immutable;

import javax.annotation.Nonnull;
import java.util.Objects;


/**
 * LicenseObject class represents a license with a canonical name and source.
 * It provides getters to access these properties.
 */
@Immutable
public class LicenseObject
{
    @JsonProperty
    private final String canonical;

    @JsonProperty
    private final String src;



    /**
     * Constructor for LicenseObject.
     *
     * @param pCanonical The canonical name of the license.
     * @param pSrc The source of the license.
     */
    @JsonCreator
    public LicenseObject(
        @JsonProperty("canonical") final String pCanonical,
        @JsonProperty("src") final String pSrc)
    {
        this.canonical = Objects.requireNonNull(pCanonical);
        this.src = Objects.requireNonNull(pSrc);
    }



    /**
     * Gets the canonical name of the license.
     *
     * @return The canonical name.
     */
    @Nonnull
    public String getCanonical()
    {
        return canonical;
    }



    /**
     * Gets the source of the license.
     *
     * @return The source URL.
     */
    @Nonnull
    public String getSrc()
    {
        return src;
    }
}
