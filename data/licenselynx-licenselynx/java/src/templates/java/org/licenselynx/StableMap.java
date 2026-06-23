/*
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;


/**
 * Holder of all the stable mappings.
 */
public final class StableMap
{
    private static final Map<String, LicenseObject> VALUES;

    static {
        Map<String, LicenseObject> m = new HashMap<>();
        /* --- CODEGEN INSERTS HERE --- */
        VALUES = Collections.unmodifiableMap(m);
    }



    private StableMap()
    {
        // static class, do not instantiate
    }



    public static Map<String, LicenseObject> getLicenseMap()
    {
        return VALUES;
    }
}
