/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
import {isScancodeLicensedbIdentifier, isSpdxIdentifier, isCustomIdentifier, isOrganizationSource, isOrganizationSourceOf, LicenseSource, Organization, map} from "../index";

const TEST_ORG = 'testOrg' as Organization;
const organizationValues = Organization as unknown as Record<string, string>;

jest.mock('../resources/merged_data.json', () => {
    return require('./resources/merged_data.json');
});

describe('LicenseLynx tests', () => {
    beforeAll(() => {
        jest.spyOn(global.console, 'error').mockImplementation(() => {
        });

        organizationValues.TestOrg = TEST_ORG;

        // Mock process.cwd to point to the ./tests directory
        jest.spyOn(process, 'cwd').mockReturnValue(require('path').resolve(__dirname, './tests'));
    });

    afterAll(() => {
        delete organizationValues.TestOrg;
        jest.restoreAllMocks();
    });

    afterEach(() => {
        jest.clearAllMocks();
    });


    it('should return data when license exists', async () => {
        return map("BSD Zero Clause").then(licenseObject => {
            expect(licenseObject).not.toBe(null);
            expect(licenseObject!.id).toEqual('0BSD');
            expect(licenseObject!.src).toEqual('spdx');
            expect(licenseObject!.src).toEqual(LicenseSource.Spdx)
            expect(isSpdxIdentifier(licenseObject)).toBe(true);
            expect(isScancodeLicensedbIdentifier(licenseObject)).toBe(false);
        });
    });

    it('should return Scancode LicenseDB data when license exists', async () => {
        return map("License only in scancode").then(licenseObject => {
            expect(licenseObject).not.toBe(null);
            expect(licenseObject!.id).toEqual('only-scancode');
            expect(licenseObject!.src).toEqual('scancode-licensedb');
            expect(licenseObject!.src).toEqual(LicenseSource.ScancodeLicensedb)
            expect(isSpdxIdentifier(licenseObject)).toBe(false);
            expect(isScancodeLicensedbIdentifier(licenseObject)).toBe(true);
        });
    });

    it('should return custom source when license exists', async () => {
        return map("Custom License").then(licenseObject => {
            expect(licenseObject).not.toBe(null);
            expect(licenseObject!.id).toEqual('custom-license');
            expect(licenseObject!.src).toEqual('custom');
            expect(licenseObject!.src).toEqual(LicenseSource.Custom)
            expect(isSpdxIdentifier(licenseObject)).toBe(false);
            expect(isScancodeLicensedbIdentifier(licenseObject)).toBe(false);
            expect(isCustomIdentifier(licenseObject)).toBe(true);
        });
    });


    it('should return normalized quotes when license exists', async () => {
        return map("BSD \u201AZero\u201B Clause").then(licenseObject => {
            expect(licenseObject).not.toBe(null);
            expect(licenseObject!.id).toEqual('0BSD');
            expect(licenseObject!.src).toEqual('spdx');
        });
    });

    it('should return data when license exists in risky map', async () => {
        return map("BSD Zero Clause Risky", true).then(licenseObject => {
            expect(licenseObject).not.toBe(null);
            expect(licenseObject!.id).toEqual('0BSD');
            expect(licenseObject!.src).toEqual('spdx');
        });
    });

    it('should return reject error when license not found', async () => {
        await expect(map('licenseNonExisting')).rejects.toEqual(new Error('License licenseNonExisting not found.'));
        return expect(map('licenseNonExisting', true)).rejects.toEqual(new Error('License licenseNonExisting not found.'));

    });

    it('should return reject error when input is null', async () => {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-expect-error
        const input: string = null
        await expect(map(input)).rejects.toEqual(new Error('License null not found.'));
        return expect(map(input, true)).rejects.toEqual(new Error('License null not found.'));

    });

    it('should return organization license when org is provided', async () => {
        return map("test-org-license", false, TEST_ORG).then(licenseObject => {
            expect(licenseObject).not.toBe(null);
            expect(licenseObject!.id).toEqual('testOrgId');
            expect(licenseObject!.src).toEqual(TEST_ORG);
            expect(isOrganizationSource(licenseObject)).toBe(true);
            expect(isOrganizationSourceOf(licenseObject, TEST_ORG)).toBe(true);
            expect(isSpdxIdentifier(licenseObject)).toBe(false);
            expect(isScancodeLicensedbIdentifier(licenseObject)).toBe(false);
            expect(isCustomIdentifier(licenseObject)).toBe(false);
        });
    });

    it('should return organization license with risky enabled', async () => {
        return map("test-org-license", true, TEST_ORG).then(licenseObject => {
            expect(licenseObject).not.toBe(null);
            expect(licenseObject!.id).toEqual('testOrgId');
            expect(licenseObject!.src).toEqual(TEST_ORG);
        });
    });

    it('should not return organization license without org parameter', async () => {
        await expect(map('test-org-license')).rejects.toEqual(new Error('License test-org-license not found.'));
        return expect(map('test-org-license', true)).rejects.toEqual(new Error('License test-org-license not found.'));
    });

    it('should reject when organization license does not exist', async () => {
        return expect(map('nonExistingOrgLicense', false, TEST_ORG)).rejects.toEqual(new Error('License nonExistingOrgLicense not found.'));
    });

    it('should return false for isOrganizationSource on spdx license', async () => {
        return map("BSD Zero Clause").then(licenseObject => {
            expect(isOrganizationSource(licenseObject)).toBe(false);
            expect(isOrganizationSourceOf(licenseObject, TEST_ORG)).toBe(false);
        });
    });

    it('should reject when organization map does not exist in data', async () => {
        const unknownOrg = 'unknown-org' as Organization;
        return expect(map('test-org-license', false, unknownOrg)).rejects.toEqual(new Error('License test-org-license not found.'));
    });

    it('should reject when license data has empty id', async () => {
        return expect(map('Incomplete License')).rejects.toEqual(new Error('License Incomplete License not found.'));
    });
});
