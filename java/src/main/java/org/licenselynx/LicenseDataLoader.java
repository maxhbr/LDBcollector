package com.siemens.licenselynx;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import com.siemens.licenselynx.dto.LicenseMap;
import com.siemens.licenselynx.dto.LicenseObject;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.util.Map;
import java.util.Objects;


/**
 * Loads license data from a JSON file.
 */
public class LicenseDataLoader
    implements LicenseDataProvider
{

    private static final Logger LOGGER = LoggerFactory.getLogger(LicenseDataLoader.class);

    private static final String RESOURCE_NAME = "merged_data.json";



    @Override
    public LicenseMap loadLicenses()
    {
        try (
            BufferedInputStream bufferedInputStream = new BufferedInputStream(
                Objects.requireNonNull(LicenseLynx.class.getClassLoader().getResourceAsStream(RESOURCE_NAME))))
        {
            ObjectMapper objectMapper = new ObjectMapper();

            LicenseMap licenseMap = new LicenseMap(objectMapper.readValue(bufferedInputStream,
                new TypeReference<Map<String, LicenseObject>>(){}));

            LOGGER.info("Successfully loaded license mappings");
            return licenseMap;
        }
        catch (IOException e) {
            LOGGER.error("Failed to read JSON file", e);
            return null;
        }
    }
}
