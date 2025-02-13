package com.siemens.licenselynx;

import com.siemens.licenselynx.dto.LicenseObject;

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
        String licenseName = "BSD Zero Clause";

        // Act
        LicenseObject result = LicenseLynx.map(licenseName);

        // Assert
        assert result != null;
        Assertions.assertEquals("0BSD", result.getCanonical());
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

}
