/*
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

/**
 * Common interface for all canonical license source types.
 * Both {@link LicenseSource} and {@link Organization} implement this interface,
 * allowing them to be used interchangeably as the source of a license.
 */
public interface CanonicalSource
{
    /**
     * Gets the string value of this source.
     *
     * @return The string representation.
     */
    String getValue();
}
