/*
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import javax.annotation.Nonnull;


/**
 * Deserializer for {@link CanonicalSource}.
 * Attempts to resolve the value first as a {@link LicenseSource}, then as an {@link Organization}.
 */
final class CanonicalSourceDeserializer
{
    private CanonicalSourceDeserializer()
    {
        // utility class
    }



    /**
     * Parses a string value to a CanonicalSource.
     * Tries LicenseSource first, then Organization.
     *
     * @param pValue The string value to parse.
     * @return The corresponding CanonicalSource.
     * @throws IllegalArgumentException if the value is unknown.
     */
    @Nonnull
    public static CanonicalSource fromValue(@Nonnull final String pValue)
    {
        // Try LicenseSource first
        for (LicenseSource source : LicenseSource.values())
        {
            if (source.getValue().equals(pValue))
            {
                return source;
            }
        }

        // Try Organization
        for (Organization org : Organization.values())
        {
            if (org.getValue().equals(pValue))
            {
                return org;
            }
        }

        throw new IllegalArgumentException("Unknown canonical source: " + pValue);
    }
}
