package com.siemens.licenselynx;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;

import org.junit.jupiter.api.Assertions;

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
        String result = LicenseLynx.map(licenseName);

        // Assert
        Assertions.assertEquals("Afmparse", result);
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
        String result = LicenseLynx.map(licenseName);

        // Assert
        Assertions.assertNull(result);
    }
}
