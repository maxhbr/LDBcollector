declare module '@sbom/licenselynx' {
    export interface LicenseObject {
        readonly canonical: string;
        readonly src: string;
    }

    export function map(licenseName: string): LicenseObject;
}
