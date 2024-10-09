export class LicenseObject {
    private readonly canonical: string;
    private readonly src: string;

    constructor(canonical: string, src: string) {
        this.canonical = canonical;
        this.src = src;
    }

    getCanonical(): string {
        return this.canonical;
    }

    getSrc(): string {
        return this.src;
    }
}
