/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: Apache-2.0
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
    void testMapCanonicalLicense()
    {
        // Arrange
        String licenseName = "test-license";

        // Act
        LicenseObject result = LicenseLynx.map(licenseName);

        // Assert
        assert result != null;
        Assertions.assertEquals(result.getCanonical(), "testCanonical");
        Assertions.assertEquals(result.getSrc(), "testSrc");
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
        Assertions.assertEquals(result.getCanonical(), "testCanonical");
        Assertions.assertEquals(result.getSrc(), "testSrc");
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

        testMap.put("test", new LicenseObject("TestCanonical", "TestSrc"));
        testRiskyMap.put("testRisky", new LicenseObject("TestCanonicalRisky", "TestSrcRisky"));

        LicenseMap licenseMap = new LicenseMap(testMap, testRiskyMap);
        LicenseMapSingleton testInstance = new LicenseMapSingleton(licenseMap);

        Assertions.assertEquals("TestCanonical",
            testInstance.getLicenseMap().getCanonicalLicenseMap().get("test").getCanonical());
        Assertions.assertEquals("TestSrc", testInstance.getLicenseMap().getCanonicalLicenseMap().get("test").getSrc());
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
}
