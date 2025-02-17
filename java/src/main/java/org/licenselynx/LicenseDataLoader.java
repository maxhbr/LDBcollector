package com.siemens.licenselynx;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.annotation.Nonnull;
import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.Map;
import java.util.Objects;


/**
 * Loads license data from a JSON file.
 */
class LicenseDataLoader
{

    private static final Logger LOGGER = LoggerFactory.getLogger(LicenseDataLoader.class);

    private static final String RESOURCE_NAME = "merged_data.json";

    @Nonnull
    Map<String, LicenseObject> loadLicenses()
    {
        try (
            BufferedInputStream bufferedInputStream = new BufferedInputStream(
                Objects.requireNonNull(LicenseLynx.class.getClassLoader().getResourceAsStream(RESOURCE_NAME),
                    "Resource not found: " + RESOURCE_NAME))
        ) {
            ObjectMapper objectMapper = new ObjectMapper();

            Map<String, LicenseObject> licenseMap = objectMapper.readValue(bufferedInputStream,
                new TypeReference<Map<String, LicenseObject>>() {});

            LOGGER.info("Successfully loaded license mappings");
            return licenseMap;
        }
        catch (IOException e)
        {
            throw new UncheckedIOException("Failed to read JSON file: " + RESOURCE_NAME, e);
        }
    }

}
