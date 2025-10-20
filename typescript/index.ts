/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
import * as mergedData from './resources/merged_data.json';

export interface LicenseObject {
    readonly canonical: string;
    readonly src: string;
}

export interface LicenseMap {
    [licenseName: string]: LicenseObject;
}

interface LicenseRepository {
    stableMap: LicenseMap;
    riskyMap: LicenseMap;
}


/**
 * Maps the given license name to its corresponding data.
 *
 * @param licenseName the name of the license to map
 * @param risky enable risky mappings
 * @returns LicenseObject as promise or error if not found
 */
export const map = function (licenseName: string, risky: boolean = false) {
    return new Promise<LicenseObject>((resolve, reject) => {
        const licenses = mergedData as LicenseRepository;

        const normalizedLicenseName = normalizeQuotes(licenseName);

        let licenseData = licenses.stableMap[normalizedLicenseName];

        if (!licenseData && risky) {
            licenseData = licenses.riskyMap[licenseName];
        }

        if (licenseData) {
            const canonical = licenseData.canonical;
            const src = licenseData.src;

            if (canonical && src) {
                resolve(Object.freeze({canonical, src}));
            }
        }

        reject(new Error('error: License ' + licenseName + ' not found'));
    })
}

// A readonly array of quote characters to be replaced.
const QUOTE_CHARACTERS: readonly string[] = [
    // Single quotes
    '‘', // LEFT SINGLE QUOTATION MARK
    '’', // RIGHT SINGLE QUOTATION MARK
    '‚', // SINGLE LOW-9 QUOTATION MARK
    '‛', // SINGLE HIGH-REVERSED-9 QUOTATION MARK
    '′', // PRIME (often used as an apostrophe)
    '＇', // FULLWIDTH APOSTROPHE
    // Double quotes
    '“', // LEFT DOUBLE QUOTATION MARK
    '”', // RIGHT DOUBLE QUOTATION MARK
    '„', // DOUBLE LOW-9 QUOTATION MARK
    '‟', // DOUBLE HIGH-REVERSED-9 QUOTATION MARK
    '″', // DOUBLE PRIME
    '«', // LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    '»', // RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    '＂'  // FULLWIDTH QUOTATION MARK
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


