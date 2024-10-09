package com.siemens.licenselynx;

/**
 * LicenseObject class represents a license with a canonical name and source.
 * It provides getters to access these properties.
 */
public class LicenseObject
{

    private final String canonical;
    private final String src;

    /**
     * Constructor for LicenseObject.
     *
     * @param pCanonical The canonical name of the license.
     * @param pSrc The source of the license.
     */
    public LicenseObject(final String pCanonical, final String pSrc)
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
