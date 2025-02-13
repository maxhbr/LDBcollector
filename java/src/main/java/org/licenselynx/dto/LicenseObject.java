package com.siemens.licenselynx.dto;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import net.jcip.annotations.Immutable;


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
        @JsonProperty("src") String pSrc)
    {
        this.canonical = pCanonical;
        this.src = pSrc;
    }

    /**
     * Gets the canonical name of the license.
     *
     * @return The canonical name.
     */
    public String getCanonical()
    {
        return canonical;
    }

    /**
     * Gets the source of the license.
     *
     * @return The source URL.
     */
    public String getSrc()
    {
        return src;
    }
}
