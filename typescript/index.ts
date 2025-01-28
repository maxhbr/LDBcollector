import * as mergedData from './tests/resources/merged_data.json';

export interface LicenseObject {
    readonly canonical: string;
    readonly src: string;
}

interface LicenseRepository {
    [key: string]: LicenseObject
}


/**
 * Maps the given license name to its corresponding data.
 *
 * @param licenseName the name of the license to map
 * @returns LicenseObject as promise or error if not found
 */
export const map = function (licenseName: string) {
    return new Promise<LicenseObject>((resolve, reject) => {
        const licenses = mergedData as LicenseRepository;
        const licenseData = licenses[licenseName];

        if (licenseData) {
            const canonical = licenseData.canonical;
            const src = licenseData.src;

            if (canonical && src) {
                resolve({canonical, src});
            }
        }
        reject({error: 'License ' + licenseName + ' not found',});
    })
}


