/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

import org.mockito.junit.jupiter.MockitoExtension;
import org.junit.jupiter.api.Assertions;

import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.util.HashMap;
import java.util.Map;


/**
 * Test class for LicenseLynx.
 */
@ExtendWith(MockitoExtension.class)
class LicenseLynxTest
{
    private final String CANONICAL_ID_SPDX = "testCanonicalSpdx";
    private final String CANONICAL_ID_SCANCODE = "testCanonicalScanCode";

    /**
     * Tests mapping of a non-existing license name.
     */
    @Test
    void testMapNonExistingLicense()
    {
        // Arrange
        String licenseName = "nonExistingLicense";

        // Act
        LicenseObject result1 = LicenseLynx.map(licenseName);
        LicenseObject result2 = LicenseLynx.map(licenseName, true);
        LicenseObject result3 = LicenseLynx.map(licenseName, false);

        // Assert
        Assertions.assertNull(result1);
        Assertions.assertNull(result2);
        Assertions.assertNull(result3);

    }

    @Test
    @SuppressWarnings("deprecation")
    void testMapCanonicalLicense()
    {
        // Arrange
        String licenseNameSpdx = "test-license";
        String licenseNameScancode = "test-risky-license";

        // Act
        LicenseObject result_spdx = LicenseLynx.map(licenseNameSpdx);
        LicenseObject result_scancode = LicenseLynx.map(licenseNameScancode, true);

        // Assert
        assert result_spdx != null;
        assert result_scancode != null;
        Assertions.assertEquals(CANONICAL_ID_SPDX, result_spdx.getId());
        Assertions.assertEquals(CANONICAL_ID_SCANCODE, result_scancode.getId());

        Assertions.assertEquals(LicenseSource.Spdx, result_spdx.getLicenseSource());
        Assertions.assertEquals(LicenseSource.ScancodeLicensedb, result_scancode.getLicenseSource());

        Assertions.assertTrue(result_spdx.isSpdxIdentifier());
        Assertions.assertFalse(result_spdx.isScanCodeLicenseDbIdentifier());

        Assertions.assertTrue(result_scancode.isScanCodeLicenseDbIdentifier());
        Assertions.assertFalse(result_scancode.isSpdxIdentifier());

        Assertions.assertEquals(LicenseSource.Spdx.getValue(), result_spdx.getSrc());

    }

    @Test
    void testMapQuotesLicense()
    {
        // Arrange
        String licenseName = "‚test-license‛";

        // Act
        LicenseObject result = LicenseLynx.map(licenseName);

        // Assert
        assert result != null;
        Assertions.assertEquals(CANONICAL_ID_SPDX, result.getId());
        Assertions.assertEquals(LicenseSource.Spdx, result.getLicenseSource());
    }


    @Test
    void testMapRiskyLicense()
    {
        // Arrange
        String licenseName = "test-risky-license";

        // Act
        LicenseObject result = LicenseLynx.map(licenseName, true);

        // Assert
        assert result != null;
        Assertions.assertEquals(CANONICAL_ID_SCANCODE, result.getId());
        Assertions.assertEquals(LicenseSource.ScancodeLicensedb, result.getLicenseSource());
    }


    @Test
    void testMapRiskyLicenseNotEnabled()
    {
        // Arrange
        String licenseName = "test-risky-license";

        // Act
        LicenseObject result1 = LicenseLynx.map(licenseName, false);
        LicenseObject result2 = LicenseLynx.map(licenseName);

        // Assert
        assert result1 == null;
        assert result2 == null;
    }



    @Test
    void testWithInjectedLicenseMap()
    {
        Map<String, LicenseObject> testMap = new HashMap<>();
        Map<String, LicenseObject> testRiskyMap = new HashMap<>();

        testMap.put("test", new LicenseObject(CANONICAL_ID_SPDX, "spdx"));
        String testCanonicalRisky = "TestCanonicalRisky";
        testRiskyMap.put("testRisky", new LicenseObject(testCanonicalRisky, LicenseSource.Custom));

        LicenseMap licenseMap = new LicenseMap(testMap, testRiskyMap);
        LicenseMapSingleton testInstance = new LicenseMapSingleton(licenseMap);

        Assertions.assertEquals(CANONICAL_ID_SPDX,
            testInstance.getLicenseMap().getCanonicalLicenseMap().get("test").getId());
        Assertions.assertEquals(LicenseSource.Spdx,
                testInstance.getLicenseMap().getCanonicalLicenseMap().get("test").getLicenseSource());

        Assertions.assertEquals(LicenseSource.Custom,
                testInstance.getLicenseMap().getRiskyLicenseMap().get("testRisky").getLicenseSource());
        Assertions.assertTrue(testInstance.getLicenseMap().getRiskyLicenseMap().get("testRisky").isCustomSource());
    }



    @Test
    void testValidSingletonInstance()
    {
        // Ensure getInstance() returns the same object
        LicenseMapSingleton instance1 = LicenseMapSingleton.getInstance();
        LicenseMapSingleton instance2 = LicenseMapSingleton.getInstance();

        Assertions.assertSame(instance1, instance2, "getInstance() should always return the same instance");
    }



    @Test
    void testNullInputStream()
    {
        // Arrange
        ClassLoader mockClassLoader = new ClassLoader()
        {
            @Override
            public InputStream getResourceAsStream(final String pName)
            {
                return null;
            }
        };

        LicenseDataLoader loader = new LicenseDataLoader(new ObjectMapper(), mockClassLoader);

        // Act && Assert
        Assertions.assertThrows(IllegalArgumentException.class, loader::loadLicenses);
    }



    @Test
    void testIOException()
    {
        // Arrange
        ClassLoader mockClassLoader = new ClassLoader()
        {
            @Override
            public InputStream getResourceAsStream(final String pName)
            {
                return new InputStream()
                {
                    @Override
                    public int read()
                        throws IOException
                    {
                        throw new IOException("Test IOException");
                    }
                };
            }
        };

        LicenseDataLoader loader = new LicenseDataLoader(new ObjectMapper(), mockClassLoader);

        // Act && Assert
        Assertions.assertThrows(UncheckedIOException.class, loader::loadLicenses);
    }

    @Test
    void testIllegalArgument()
    {
        // Act && Assert
        Assertions.assertThrows(IllegalArgumentException.class, () -> LicenseSource.fromValue("non-specified-source"));
    }
}
