/*
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import java.util.EnumMap;
import java.util.HashMap;
import java.util.Map;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;


/**
 * Test class for LicenseLynx.
 */
@ExtendWith(MockitoExtension.class)
public class LicenseLynxTest
{
    private static final String CANONICAL_ID_SPDX = "testCanonicalSpdx";

    private static final String CANONICAL_ID_SCANCODE = "testCanonicalScanCode";

    private static final String CANONICAL_ID_TEST_ORG = "testOrgId";



    private LicenseMap createTestLicenseMap()
    {
        Map<String, LicenseObject> testMap = new HashMap<>();
        Map<String, LicenseObject> testRiskyMap = new HashMap<>();
        Map<Organization, Map<String, LicenseObject>> testOrgMaps = new EnumMap<>(Organization.class);

        testMap.put("test-license", new LicenseObject(CANONICAL_ID_SPDX, LicenseSource.Spdx));
        testMap.put("'test-license'", new LicenseObject(CANONICAL_ID_SPDX, LicenseSource.Spdx));
        testRiskyMap.put("test-risky-license", new LicenseObject(CANONICAL_ID_SCANCODE,
            LicenseSource.ScancodeLicensedb));

        Map<String, LicenseObject> testOrgMap = new HashMap<>();
        testOrgMap.put("test-org-license", new LicenseObject(CANONICAL_ID_TEST_ORG, Organization.Siemens));
        testOrgMaps.put(Organization.Siemens, testOrgMap);

        return new LicenseMap(testMap, testRiskyMap, testOrgMaps);
    }



    /**
     * Tests mapping of a non-existing license name.
     */
    @Test
    public void testMapNonExistingLicense()
    {
        // Arrange
        String licenseName = "nonExistingLicense";
        LicenseMap licenseMap = createTestLicenseMap();

        // Act
        LicenseObject result1 = LicenseLynx.map(licenseName, false, null, licenseMap);
        LicenseObject result2 = LicenseLynx.map(licenseName, true, null, licenseMap);
        LicenseObject result3 = LicenseLynx.map(licenseName, false, Organization.Siemens, licenseMap);
        LicenseObject result4 = LicenseLynx.map(licenseName, true, Organization.Siemens, licenseMap);

        // Assert
        Assertions.assertNull(result1);
        Assertions.assertNull(result2);
        Assertions.assertNull(result3);
        Assertions.assertNull(result4);
    }



    @Test
    @SuppressWarnings("deprecation")
    public void testMapCanonicalLicense()
    {
        // Arrange
        String licenseNameSpdx = "test-license";
        String licenseNameScancode = "test-risky-license";
        LicenseMap licenseMap = createTestLicenseMap();

        // Act
        LicenseObject resultSpdx = LicenseLynx.map(licenseNameSpdx, false, null, licenseMap);
        LicenseObject resultScancode = LicenseLynx.map(licenseNameScancode, true, null, licenseMap);
        LicenseObject resultSpdxRisky = LicenseLynx.map(licenseNameSpdx, true, null, licenseMap);

        // Assert
        assert resultSpdx != null;
        assert resultScancode != null;
        Assertions.assertNotNull(resultSpdxRisky);
        Assertions.assertEquals(CANONICAL_ID_SPDX, resultSpdxRisky.getId());
        Assertions.assertEquals(CANONICAL_ID_SPDX, resultSpdx.getId());
        Assertions.assertEquals(CANONICAL_ID_SCANCODE, resultScancode.getId());

        Assertions.assertEquals(LicenseSource.Spdx, resultSpdx.getCanonicalSource());
        Assertions.assertEquals(LicenseSource.ScancodeLicensedb, resultScancode.getCanonicalSource());

        Assertions.assertTrue(resultSpdx.isSpdxIdentifier());
        Assertions.assertFalse(resultSpdx.isScanCodeLicenseDbIdentifier());

        Assertions.assertTrue(resultScancode.isScanCodeLicenseDbIdentifier());
        Assertions.assertFalse(resultScancode.isSpdxIdentifier());

        Assertions.assertEquals(LicenseSource.Spdx.getValue(), resultSpdx.getSrc());
    }



    @Test
    public void testMapQuotesLicense()
    {
        // Arrange
        String licenseName = "‚test-license‛";
        LicenseMap licenseMap = createTestLicenseMap();

        // Act
        LicenseObject result = LicenseLynx.map(licenseName, false, null, licenseMap);

        // Assert
        assert result != null;
        Assertions.assertEquals(CANONICAL_ID_SPDX, result.getId());
        Assertions.assertEquals(LicenseSource.Spdx, result.getCanonicalSource());
    }



    @Test
    @SuppressWarnings("ConstantValue")
    public void testNormalizeQuotesNullInput()
    {
        // Arrange && Act
        String result = QuotesHandler.normalizeQuotes(null, "'");

        // Assert
        Assertions.assertNull(result);
    }



    @Test
    public void testMapRiskyLicense()
    {
        // Arrange
        String licenseName = "test-risky-license";
        LicenseMap licenseMap = createTestLicenseMap();

        // Act
        LicenseObject result = LicenseLynx.map(licenseName, true, null, licenseMap);

        // Assert
        assert result != null;
        Assertions.assertEquals(CANONICAL_ID_SCANCODE, result.getId());
        Assertions.assertEquals(LicenseSource.ScancodeLicensedb, result.getCanonicalSource());
    }



    @Test
    public void testMapRiskyLicenseNotEnabled()
    {
        // Arrange
        String licenseName = "test-risky-license";
        LicenseMap licenseMap = createTestLicenseMap();

        // Act
        LicenseObject result1 = LicenseLynx.map(licenseName, false, null, licenseMap);
        LicenseObject result2 = LicenseLynx.map(licenseName, false, Organization.Siemens, licenseMap);

        // Assert
        assert result1 == null;
        assert result2 == null;
    }



    @Test
    @SuppressWarnings("deprecation")
    public void testWithInjectedLicenseMap()
    {
        // Arrange
        Map<String, LicenseObject> testMap = new HashMap<>();
        Map<String, LicenseObject> testRiskyMap = new HashMap<>();

        testMap.put("test", new LicenseObject(CANONICAL_ID_SPDX, "spdx"));
        String testCanonicalRisky = "TestCanonicalRisky";
        testRiskyMap.put("testRisky", new LicenseObject(testCanonicalRisky, LicenseSource.Custom));

        LicenseMap licenseMap = new LicenseMap(testMap, testRiskyMap, new EnumMap<>(Organization.class));

        // Act && Assert
        Assertions.assertEquals(CANONICAL_ID_SPDX,
            licenseMap.getCanonicalLicenseMap().get("test").getId());
        Assertions.assertEquals(LicenseSource.Spdx,
            licenseMap.getCanonicalLicenseMap().get("test").getCanonicalSource());

        Assertions.assertEquals(LicenseSource.Custom,
            licenseMap.getRiskyLicenseMap().get("testRisky").getCanonicalSource());
        Assertions.assertTrue(licenseMap.getRiskyLicenseMap().get("testRisky").isCustomSource());
    }



    @Test
    public void testLicenseSourceFromValue()
    {
        // Act && Assert
        Assertions.assertEquals(LicenseSource.Spdx, LicenseSource.fromValue("spdx"));
        Assertions.assertEquals(LicenseSource.ScancodeLicensedb, LicenseSource.fromValue("scancode-licensedb"));
        Assertions.assertEquals(LicenseSource.Custom, LicenseSource.fromValue("custom"));
    }



    @Test
    public void testIllegalArgument()
    {
        // Act && Assert
        Assertions.assertThrows(IllegalArgumentException.class, () -> LicenseSource.fromValue("non-specified-source"));
    }



    @Test
    public void testOrganizationSource()
    {
        // Arrange
        LicenseObject orgLicense = new LicenseObject(CANONICAL_ID_TEST_ORG, Organization.Siemens);

        // Act && Assert
        Assertions.assertEquals(CANONICAL_ID_TEST_ORG, orgLicense.getId());
        Assertions.assertEquals(Organization.Siemens, orgLicense.getCanonicalSource());
        Assertions.assertTrue(orgLicense.isOrganizationSource());
        Assertions.assertTrue(orgLicense.isOrganizationSource(Organization.Siemens));
        Assertions.assertFalse(orgLicense.isSpdxIdentifier());
        Assertions.assertFalse(orgLicense.isScanCodeLicenseDbIdentifier());
        Assertions.assertFalse(orgLicense.isCustomSource());
    }



    @Test
    @SuppressWarnings("deprecation")
    public void testOrganizationSourceFromString()
    {
        // Arrange && Act
        LicenseObject orgLicense = new LicenseObject(CANONICAL_ID_TEST_ORG, "siemens");

        // Assert
        Assertions.assertEquals(CANONICAL_ID_TEST_ORG, orgLicense.getId());
        Assertions.assertEquals(Organization.Siemens, orgLicense.getCanonicalSource());
        Assertions.assertTrue(orgLicense.isOrganizationSource());
        Assertions.assertEquals("siemens", orgLicense.getSrc());
    }



    @Test
    @SuppressWarnings("deprecation")
    public void testDeprecatedGetLicenseSourceWithLicenseSource()
    {
        // Arrange
        LicenseObject spdxLicense = new LicenseObject("MIT", LicenseSource.Spdx);

        // Act & Assert
        Assertions.assertEquals(LicenseSource.Spdx, spdxLicense.getLicenseSource());
    }



    @Test
    @SuppressWarnings("deprecation")
    public void testDeprecatedGetLicenseSourceWithOrganization()
    {
        // Arrange
        LicenseObject orgLicense = new LicenseObject(CANONICAL_ID_TEST_ORG, Organization.Siemens);

        // Act && Assert
        Assertions.assertThrows(ClassCastException.class, orgLicense::getLicenseSource);
    }



    @Test
    public void testNotOrganizationSource()
    {
        // Arrange
        LicenseObject spdxLicense = new LicenseObject("MIT", LicenseSource.Spdx);

        // Assert
        Assertions.assertFalse(spdxLicense.isOrganizationSource());
        Assertions.assertFalse(spdxLicense.isOrganizationSource(Organization.Siemens));
    }



    @Test
    public void testUnknownCanonicalSource()
    {
        // Act && Assert
        Assertions.assertThrows(IllegalArgumentException.class,
            () -> CanonicalSourceDeserializer.fromValue("unknown-source"));
    }



    @Test
    public void testOrganizationFromValue()
    {
        // Act & Assert
        Assertions.assertEquals(Organization.Siemens, Organization.fromValue("siemens"));
        Assertions.assertThrows(IllegalArgumentException.class, () -> Organization.fromValue("unknown-org"));
    }



    @Test
    @SuppressWarnings("MismatchedQueryAndUpdateOfCollection")
    public void testWithInjectedLicenseMapWithOrgs()
    {
        // Arrange
        Map<String, LicenseObject> testMap = new HashMap<>();
        Map<String, LicenseObject> testRiskyMap = new HashMap<>();
        Map<Organization, Map<String, LicenseObject>> testOrgMaps = new EnumMap<>(Organization.class);

        testMap.put("test", new LicenseObject(CANONICAL_ID_SPDX, LicenseSource.Spdx));

        Map<String, LicenseObject> testOrgMap = new HashMap<>();
        testOrgMap.put("test-org-license", new LicenseObject(CANONICAL_ID_TEST_ORG, Organization.Siemens));
        testOrgMaps.put(Organization.Siemens, testOrgMap);

        LicenseMap licenseMap = new LicenseMap(testMap, testRiskyMap, testOrgMaps);

        // Act && Assert
        Assertions.assertEquals(CANONICAL_ID_TEST_ORG,
            licenseMap.getOrganizationMap(Organization.Siemens).get("test-org-license").getId());
        Assertions.assertEquals(Organization.Siemens,
            licenseMap.getOrganizationMap(Organization.Siemens).get("test-org-license").getCanonicalSource());
        Assertions.assertTrue(licenseMap.getOrganizationMaps().containsKey(Organization.Siemens));
    }



    @Test
    public void testOrganizationMapEmpty()
    {
        // Arrange
        Map<String, LicenseObject> testMap = new HashMap<>();
        Map<String, LicenseObject> testRiskyMap = new HashMap<>();
        LicenseMap licenseMap = new LicenseMap(testMap, testRiskyMap, new EnumMap<>(Organization.class));

        // Act && Assert
        Assertions.assertNotNull(licenseMap.getOrganizationMap(Organization.Siemens));
        Assertions.assertTrue(licenseMap.getOrganizationMap(Organization.Siemens).isEmpty());
    }



    @Test
    public void testMapWithOrganization()
    {
        // Arrange
        String licenseName = "test-org-license";
        LicenseMap licenseMap = createTestLicenseMap();

        // Act
        LicenseObject result = LicenseLynx.map(licenseName, false, Organization.Siemens, licenseMap);

        // Assert
        Assertions.assertNotNull(result);
        Assertions.assertEquals(CANONICAL_ID_TEST_ORG, result.getId());
        Assertions.assertEquals(Organization.Siemens, result.getCanonicalSource());
        Assertions.assertTrue(result.isOrganizationSource());
        Assertions.assertTrue(result.isOrganizationSource(Organization.Siemens));
    }



    @Test
    public void testMapWithOrganizationAndRisky()
    {
        // Arrange
        String licenseName = "test-org-license";
        LicenseMap licenseMap = createTestLicenseMap();

        // Act
        LicenseObject result = LicenseLynx.map(licenseName, true, Organization.Siemens, licenseMap);

        // Assert
        Assertions.assertNotNull(result);
        Assertions.assertEquals(CANONICAL_ID_TEST_ORG, result.getId());
        Assertions.assertEquals(Organization.Siemens, result.getCanonicalSource());
    }



    @Test
    public void testMapOrganizationLicenseNotFoundWithoutOrg()
    {
        // Arrange
        String licenseName = "test-org-license";
        LicenseMap licenseMap = createTestLicenseMap();

        // Act
        LicenseObject result1 = LicenseLynx.map(licenseName, false, null, licenseMap);
        LicenseObject result2 = LicenseLynx.map(licenseName, true, null, licenseMap);

        // Assert
        Assertions.assertNull(result1);
        Assertions.assertNull(result2);
    }



    @Test
    public void testMapNonExistingOrgLicense()
    {
        // Arrange
        String licenseName = "nonExistingOrgLicense";
        LicenseMap licenseMap = createTestLicenseMap();

        // Act
        LicenseObject result = LicenseLynx.map(licenseName, false, Organization.Siemens, licenseMap);

        // Assert
        Assertions.assertNull(result);
    }
}
