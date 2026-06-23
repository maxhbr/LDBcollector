/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
import * as mergedData from './resources/merged_data.json';

export interface LicenseObject {
    readonly id: string;
    readonly src: string;
}

export interface LicenseMap {
    [licenseName: string]: LicenseObject;
}

export enum LicenseSource {
    Spdx = 'spdx',
    ScancodeLicensedb = 'scancode-licensedb',
    Custom = 'custom',
}

export enum Organization {
    Siemens = 'siemens',
}

interface LicenseRepository {
    stableMap: LicenseMap;
    riskyMap: LicenseMap;
    [key: string]: LicenseMap;
}


/**
 * Maps the given license name to its corresponding data.
 *
 * @param licenseName the name of the license to map
 * @param risky enable risky mappings
 * @param org optional organization to search in
 * @returns LicenseObject as promise or error if not found
 */
export const map = function (licenseName: string, risky: boolean = false, org?: Organization) {
    return new Promise<LicenseObject>((resolve, reject) => {
        const licenses = mergedData as LicenseRepository;

        const normalizedLicenseName = normalizeQuotes(licenseName);

        let licenseData = licenses.stableMap[normalizedLicenseName];

        if (!licenseData && risky) {
            licenseData = licenses.riskyMap[normalizedLicenseName];
        }

        if (!licenseData && org) {
            const orgMap = licenses[org as string];
            if (orgMap) {
                licenseData = orgMap[normalizedLicenseName];
            }
        }

        if (licenseData) {
            const canonical = licenseData.id;
            const src = licenseData.src;

            if (canonical && src) {
                resolve(Object.freeze({id: canonical, src}));
            }
        }

        reject(new Error('License ' + licenseName + ' not found.'));
    })
}

export const isSpdxIdentifier= function (licenseObject: LicenseObject): boolean {
    return licenseObject.src === LicenseSource.Spdx;
}

export const isScancodeLicensedbIdentifier= function (licenseObject: LicenseObject): boolean {
    return licenseObject.src === LicenseSource.ScancodeLicensedb;
}

export const isCustomIdentifier= function (licenseObject: LicenseObject): boolean {
    return licenseObject.src === LicenseSource.Custom;
}

export const isOrganizationSource = function (licenseObject: LicenseObject): boolean {
    return Object.values(Organization).includes(licenseObject.src as Organization);
}

export const isOrganizationSourceOf = function (licenseObject: LicenseObject, org: Organization): boolean {
    return licenseObject.src === org;
}


// A readonly array of quote characters to be replaced.
const QUOTE_CHARACTERS: readonly string[] = [
    // Single quotes
    '\u2018', // LEFT SINGLE QUOTATION MARK
    '\u2019', // RIGHT SINGLE QUOTATION MARK
    '\u201A', // SINGLE LOW-9 QUOTATION MARK
    '\u201B', // SINGLE HIGH-REVERSED-9 QUOTATION MARK
    '\u2032', // PRIME (often used as an apostrophe)
    '\uFF07', // FULLWIDTH APOSTROPHE
    // Double quotes
    '\u201C', // LEFT DOUBLE QUOTATION MARK
    '\u201D', // RIGHT DOUBLE QUOTATION MARK
    '\u201E', // DOUBLE LOW-9 QUOTATION MARK
    '\u201F', // DOUBLE HIGH-REVERSED-9 QUOTATION MARK
    '\u2033', // DOUBLE PRIME
    '\u00AB', // LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    '\u00BB', // RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    '\uFF02'  // FULLWIDTH QUOTATION MARK
];

/**
 * Checks if a given character is a recognized quote character.
 *
 * @param char - The character to check.
 * @returns True if the character is a quote character, false otherwise.
 */
const isQuoteCharacter = (char: string): boolean => {
    return QUOTE_CHARACTERS.includes(char);
};

/**
 * Normalizes an input string by replacing recognized Unicode quote characters
 * with a specified replacement string.
 *
 * @param input - The input string that may contain various quote characters.
 * @param replacement - The string to replace the quote characters. Defaults to "'".
 * @returns The normalized string with replaced quote characters.
 */
const normalizeQuotes = (input: string, replacement: string = "'"): string => {
    if (!input) return input;

    return input
        .split("")
        .map(char => isQuoteCharacter(char) ? replacement : char)
        .join("");
};
