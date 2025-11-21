/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
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
    private final String id;

    @JsonProperty
    private final String src;



    /**
     * Constructor for LicenseObject.
     *
     * @param pId The canonical id of the license.
     * @param pSrc The source of the license.
     */
    @JsonCreator
    public LicenseObject(
        @JsonProperty("id") final String pId,
        @JsonProperty("src") final String pSrc)
    {
        this.id = Objects.requireNonNull(pId);
        this.src = Objects.requireNonNull(pSrc);
    }



    /**
     * Gets the canonical id of the license.
     *
     * @return The canonical id.
     */
    @Nonnull
    public String getId()
    {
        return id;
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
