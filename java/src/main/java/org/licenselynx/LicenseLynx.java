package com.siemens.licenselynx;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.io.InputStream;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;


/**
 * LicenseLynx class to map license names to their corresponding data from a JSON file.
 */
public final class LicenseLynx
{

    private static final Logger LOGGER = LogManager.getLogger(LicenseLynx.class);

    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    private static final String RESOURCE_NAME = "merged_data.json";



    // Private constructor to prevent instantiation
    private LicenseLynx()
    {
    }



    /**
     * Maps the given license name to its corresponding data.
     *
     * @param pLicenseName the name of the license to map
     * @return the license data as a LicenseObject, or null if not found
     */
    public static LicenseObject map(final String pLicenseName)
    {
        return map(pLicenseName, LicenseLynx.class.getClassLoader());
    }



    /**
     * Maps the given license name to its corresponding data using the provided ClassLoader.
     * This method is primarily for testing purposes.
     *
     * @param pLicenseName the name of the license to map
     * @param pClassLoader the ClassLoader to use for resource loading
     * @return the license data as a LicenseObject, or null if not found
     */
    static LicenseObject map(final String pLicenseName, final ClassLoader pClassLoader)
    {
        try {
            try (InputStream inputStream = pClassLoader.getResourceAsStream(RESOURCE_NAME)) {
                if (inputStream != null) {
                    JsonNode mergedData = OBJECT_MAPPER.readTree(inputStream);

                    JsonNode licenseData = mergedData.get(pLicenseName);

                    if (licenseData != null) {
                        // Retrieve the canonical and src fields
                        String canonical = licenseData.get("canonical").asText();
                        String src = licenseData.get("src").asText();

                        // Return a new LicenseObject containing canonical and src
                        return new LicenseObject(canonical, src);
                    }
                    else {
                        LOGGER.error("License not found");
                        return null;
                    }
                }
                else {
                    LOGGER.error("Input stream is null");
                    return null;
                }
            }
        }
        catch (IOException e) {
            LOGGER.error("Failed to read JSON file");
            LOGGER.error(e.getMessage());
            return null;
        }
    }
}
