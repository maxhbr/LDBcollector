/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: Apache-2.0
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
        let licenseData = licenses.stableMap[licenseName];

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


