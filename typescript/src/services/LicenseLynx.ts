import * as fs from 'fs';
import { LicenseObject } from '../models/LicenseObject';

export class LicenseLynx {
    private static readonly RESOURCE_PATH = 'src/resources/merged_data.json';


    /**
     * Maps the given license name to its corresponding data.
     *
     * @param licenseName the name of the license to map
     * @returns the license data as a LicenseObject, or null if not found
     */
    public static map(licenseName: string): LicenseObject | null {
        try {
            const mergedData = JSON.parse(
                fs.readFileSync(this.RESOURCE_PATH, 'utf8')
            );

            const licenseData = mergedData[licenseName];

            if (licenseData) {
                const canonical = licenseData.canonical;
                const src = licenseData.src;

                if (canonical && src) {
                    return new LicenseObject(canonical, src);
                }
            }

            console.error('License not found');
            return null;
        } catch (error) {
            console.error('Failed to read JSON file', error as Error);
            return null;
        }
    }
}
