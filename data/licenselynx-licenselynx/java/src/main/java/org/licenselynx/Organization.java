/*
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

/**
 * Enum representing organizations which can also be canonical sources for license identifiers.
 */
public enum Organization
    implements CanonicalSource
{
    Siemens("siemens");

    // NOTE: For each enum value, an entry must be present in CustomOrgMap.

    private final String value;



    Organization(final String pValue)
    {
        this.value = pValue;
    }



    @Override
    public String getValue()
    {
        return value;
    }



    /**
     * Parses a string value to an Organization enum.
     *
     * @param pValue The string value to parse.
     * @return The corresponding Organization.
     * @throws IllegalArgumentException if the value is unknown.
     */
    public static Organization fromValue(final String pValue)
    {
        for (Organization organization : values()) {
            if (organization.value.equals(pValue)) {
                return organization;
            }
        }
        throw new IllegalArgumentException("Unknown organization: " + pValue);
    }
}
