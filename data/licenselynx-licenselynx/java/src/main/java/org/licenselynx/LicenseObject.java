/*
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import java.util.Objects;
import javax.annotation.Nonnull;

import net.jcip.annotations.Immutable;


/**
 * LicenseObject class represents a license with a canonical name and source.
 * It provides getters to access these properties.
 */
@Immutable
public class LicenseObject
{
    private final String id;

    private final CanonicalSource src;



    /**
     * Constructor for LicenseObject.
     *
     * @param pId The canonical id of the license.
     * @param pSrc The source of the license as a string.
     * @deprecated Use {@link #LicenseObject(String, CanonicalSource)} instead
     */
    @Deprecated
    public LicenseObject(final String pId, final String pSrc)
    {
        this.id = Objects.requireNonNull(pId);
        this.src = CanonicalSourceDeserializer.fromValue(Objects.requireNonNull(pSrc));
    }



    /**
     * Constructor for LicenseObject.
     *
     * @param pId The canonical id of the license.
     * @param pLicenseSrc The source of the license.
     */
    public LicenseObject(final String pId, final LicenseSource pLicenseSrc)
    {
        this.id = Objects.requireNonNull(pId);
        this.src = Objects.requireNonNull(pLicenseSrc);
    }



    /**
     * Constructor for LicenseObject.
     *
     * @param pId The canonical id of the license.
     * @param pCanonicalSrc The canonical source of the license.
     */
    public LicenseObject(final String pId, final CanonicalSource pCanonicalSrc)
    {
        this.id = Objects.requireNonNull(pId);
        this.src = Objects.requireNonNull(pCanonicalSrc);
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
     * Gets the source of the license as a string.
     *
     * @return The source string value.
     *
     * @deprecated Use {@link #getCanonicalSource()} instead
     */
    @Nonnull
    @Deprecated
    public String getSrc()
    {
        return src.getValue();
    }



    /**
     * Gets the source of the license as a LicenseSource enum.
     *
     * @return The LicenseSource.
     *
     * @throws ClassCastException if the source is not a LicenseSource (e.g. it's an Organization).
     * @deprecated Use {@link #getCanonicalSource()} instead
     */
    @Nonnull
    @Deprecated
    public LicenseSource getLicenseSource()
    {
        if (src instanceof LicenseSource) {
            return (LicenseSource) src;
        }
        throw new ClassCastException(
            "Source '" + src.getValue() + "' is not a LicenseSource. Use getCanonicalSource() instead.");
    }



    /**
     * Gets the canonical source of the license.
     *
     * @return The canonical source (either a {@link LicenseSource} or an {@link Organization}).
     */
    @Nonnull
    public CanonicalSource getCanonicalSource()
    {
        return src;
    }



    /**
     * Checks if the canonical identifier used in this <code>LicenseObject</code> is one from the SPDX License List.
     *
     * @return true if source of LicenseObject is SPDX, false otherwise.
     */
    public boolean isSpdxIdentifier()
    {
        return this.src.equals(LicenseSource.Spdx);
    }



    /**
     * Checks if the canonical identifier used in this <code>LicenseObject</code> is one from the Scancode LicenseDB,
     * and not an SPDX identifier.
     *
     * @return true if source of LicenseObject is Scancode LicenseDB, false otherwise.
     */
    public boolean isScanCodeLicenseDbIdentifier()
    {
        return this.src.equals(LicenseSource.ScancodeLicensedb);
    }



    /**
     * Checks if the canonical identifier used in this <code>LicenseObject</code> is one from a custom source.
     *
     * @return true if source of LicenseObject is Custom, false otherwise.
     */
    public boolean isCustomSource()
    {
        return this.src.equals(LicenseSource.Custom);
    }



    /**
     * Checks if the canonical identifier used in this <code>LicenseObject</code> is from an organization source.
     *
     * @return true if source of LicenseObject is an Organization, false otherwise.
     */
    public boolean isOrganizationSource()
    {
        return this.src instanceof Organization;
    }



    /**
     * Checks if the canonical identifier used in this <code>LicenseObject</code> is from a specific organization.
     *
     * @param pOrganization The organization to check against.
     * @return true if source matches the given organization, false otherwise.
     */
    public boolean isOrganizationSource(@Nonnull final Organization pOrganization)
    {
        return this.src.equals(pOrganization);
    }
}
