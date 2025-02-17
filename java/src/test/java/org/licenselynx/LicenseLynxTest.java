package com.siemens.licenselynx;

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
        LicenseObject result = LicenseLynx.map(licenseName);

        // Assert
        Assertions.assertNull(result);
    }



    @Test
    void testWithInjectedLicenseMap()
    {
        Map<String, LicenseObject> testMap = new HashMap<>();
        testMap.put("test", new LicenseObject("TestCanonical", "TestSrc"));
        LicenseMapSingleton testInstance = new LicenseMapSingleton(testMap);

        Assertions.assertEquals("TestCanonical", testInstance.getLicenseMap().get("test").getCanonical());
        Assertions.assertEquals("TestSrc", testInstance.getLicenseMap().get("test").getSrc());
    }



    @Test
    void testWithNullValuesInLicenseMap()
    {
        Map<String, LicenseObject> testMap = new HashMap<>();
        testMap.put("test", new LicenseObject(null, null));
        LicenseMapSingleton testInstance = new LicenseMapSingleton(testMap);

        Assertions.assertNull(testInstance.getLicenseMap().get("test").getCanonical());
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
        Assertions.assertThrows(IllegalArgumentException.class, () -> loader.loadLicenses());
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
        Assertions.assertThrows(UncheckedIOException.class, () -> loader.loadLicenses());
    }

}
