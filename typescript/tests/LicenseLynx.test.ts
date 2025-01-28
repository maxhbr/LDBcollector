import {map} from "../index";

jest.mock('fs', () => ({
    readFileSync: jest.fn(),
}));

describe('LicenseLynx tests', () => {
    beforeAll(() => {
        jest.spyOn(global.console, 'error').mockImplementation(() => {
        });
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    it('should return data when license exists', async () => {
        return map("BSD Zero Clause").then(licenseObject => {
            expect(licenseObject).not.toBe(null);
            expect(licenseObject!.canonical).toEqual('0BSD');
            expect(licenseObject!.src).toEqual('spdx');
        });
    });

    it('should return reject error when license not found', async () => {
        return expect(map('licenseNonExisting')).rejects.toEqual({error: 'License licenseNonExisting not found'});
    });
});
