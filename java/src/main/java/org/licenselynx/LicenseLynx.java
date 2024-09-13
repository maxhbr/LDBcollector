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

    // Private constructor to prevent instantiation
    private LicenseLynx()
    { }

    /**
     * Maps the given license name to its corresponding data.
     *
     * @param pLicenseName the name of the license to map
     * @return the license data as a String, or null if not found
     */
    public static String map(final String pLicenseName)
    {
        try {
            ClassLoader classLoader = LicenseLynx.class.getClassLoader();
            try (InputStream inputStream = classLoader.getResourceAsStream("merged_data.json")) {

                if (inputStream != null) {
                    JsonNode mergedData = OBJECT_MAPPER.readTree(inputStream);

                    JsonNode licenseData = mergedData.get(pLicenseName);

                    if (licenseData != null)
                    {
                        return licenseData.asText();
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
