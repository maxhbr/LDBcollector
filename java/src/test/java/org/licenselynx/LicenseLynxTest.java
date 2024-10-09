package com.siemens.licenselynx;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;
import org.junit.jupiter.api.Assertions;

import java.io.IOException;
import java.io.InputStream;


/**
 * Test class for LicenseLynx.
 */
@ExtendWith(MockitoExtension.class)
class LicenseLynxTest
{

    /**
     * Tests mapping of an existing license name.
     */
    @Test
    void testMapExistingLicense()
    {
        // Arrange
        String licenseName = "Afmparse License";

        // Act
        LicenseObject result = LicenseLynx.map(licenseName);

        // Assert
        assert result != null;
        Assertions.assertEquals("Afmparse", result.getCanonical());
        Assertions.assertEquals("spdx", result.getSrc());
    }



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



    /**
     * Tests handling of null input stream.
     */
    @Test
    void testNullInputStream()
    {
        // Arrange
        String licenseName = "Afmparse License";
        ClassLoader mockClassLoader = new ClassLoader()
        {
            @Override
            public InputStream getResourceAsStream(final String pName)
            {
                return null;
            }
        };

        // Act
        LicenseObject result = LicenseLynx.map(licenseName, mockClassLoader);

        // Assert
        Assertions.assertNull(result);
    }



    /**
     * Tests handling of IOException.
     */
    @Test
    void testIOException()
    {
        // Arrange
        String licenseName = "Afmparse License";
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

        // Act
        LicenseObject result = LicenseLynx.map(licenseName, mockClassLoader);

        // Assert
        Assertions.assertNull(result);
    }
}
