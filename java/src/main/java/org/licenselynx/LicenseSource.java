/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import com.fasterxml.jackson.annotation.JsonValue;

/**
 * Enum representing the possible sources of a license.
 */
public enum LicenseSource
{
    Spdx("spdx"),
    ScancodeLicensedb("scancode-licensedb"),
    Custom("custom");

    private final String value;

    LicenseSource(final String pValue)
    {
        this.value = pValue;
    }

    @JsonValue
    public String getValue()
    {
        return value;
    }

    /**
     * Parses a string value to a LicenseSource enum.
     *
     * @param pValue The string value to parse.
     * @return The corresponding LicenseSource.
     * @throws IllegalArgumentException if the value is unknown.
     */
    public static LicenseSource fromValue(final String pValue)
    {
        for (LicenseSource source : values())
        {
            if (source.value.equals(pValue))
            {
                return source;
            }
        }
        throw new IllegalArgumentException("Unknown license source: " + pValue);
    }
}
