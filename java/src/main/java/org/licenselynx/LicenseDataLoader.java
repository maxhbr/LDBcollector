/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: Apache-2.0
 */
package org.licenselynx;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.annotation.Nonnull;
import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;


/**
 * Loads license data from a JSON file.
 */
class LicenseDataLoader
{

    private static final Logger LOGGER = LoggerFactory.getLogger(LicenseDataLoader.class);

    private static final String RESOURCE_NAME = "merged_data.json";

    private final ObjectMapper objectMapper;

    private final ClassLoader classLoader;



    // Constructor for production code using ClassLoader by default
    LicenseDataLoader()
    {
        this(new ObjectMapper(), LicenseDataLoader.class.getClassLoader());  // Default to the system classloader
    }



    // Constructor for testability, injecting ClassLoader
    LicenseDataLoader(final ObjectMapper pObjectMapper, final ClassLoader pClassLoader)
    {
        this.objectMapper = pObjectMapper;
        this.classLoader = pClassLoader;
    }



    @Nonnull
    LicenseMap loadLicenses()
    {
        try (
            InputStream resourceStream = classLoader.getResourceAsStream(RESOURCE_NAME)
        )
        {
            if (resourceStream == null)
            {
                throw new IllegalArgumentException("Resource not found: " + RESOURCE_NAME);
            }
            try (BufferedInputStream bufferedInputStream = new BufferedInputStream(resourceStream))
            {
                LicenseMap licenseMap = objectMapper.readValue(bufferedInputStream,
                    new TypeReference<LicenseMap>()
                    {
                    });

                LOGGER.info("Successfully loaded license mappings");
                return licenseMap;
            }
        }
        catch (IOException e)
        {
            throw new UncheckedIOException("Failed to read JSON file: " + RESOURCE_NAME, e);
        }
    }
}
