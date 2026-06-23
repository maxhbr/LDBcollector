/*
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import java.util.Map;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;


/**
 * Unit tests of {@link CustomOrgMap}.
 */
public class CustomOrgMapTest
{
    /**
     * This test will fail if a new organization is added to the enum without updating the CustomOrgMap.
     */
    @Test
    public void testEnumCompleteness()
    {
        for (Organization org : Organization.values()) {
            Map<String, LicenseObject> actualOrgMap = CustomOrgMap.getOrgMaps().get(org);
            String msg = "The organization-specific map for '" + org.name()
                + "' is missing or empty. Check the CustomOrgMap class for completeness.";
            Assertions.assertNotNull(actualOrgMap, msg);
            Assertions.assertFalse(actualOrgMap.isEmpty(), msg);
        }
    }
}
