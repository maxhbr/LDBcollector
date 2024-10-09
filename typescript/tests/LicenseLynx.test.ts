import * as fs from 'fs';
import {LicenseLynx} from '../src';

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

    it('should return data when license exists', () => {
        const mockedData = {
            "BSD Zero Clause": {
                "canonical": "0BSD",
                "src": "spdx"
            }
        };
        (fs.readFileSync as jest.Mock).mockReturnValueOnce(JSON.stringify(mockedData));

        const licenseObject = LicenseLynx.map('BSD Zero Clause');

        expect(licenseObject).not.toBe(null);
        expect(licenseObject!.getCanonical()).toEqual('0BSD');
        expect(licenseObject!.getSrc()).toEqual('spdx');
    });

    it('should return error when license not found', () => {
        const mockedData = {
            "BSD Zero Clause": {
                "canonical": "0BSD",
                "src": "spdx"
            }
        };
        (fs.readFileSync as jest.Mock).mockReturnValueOnce(JSON.stringify(mockedData));

        const licenseObject = LicenseLynx.map('licenseNonExisting');

        expect(licenseObject).toBe(null);
        expect(console.error).toHaveBeenCalled();
    });

    it('should return error when failed to read data', () => {
        (fs.readFileSync as jest.Mock).mockImplementationOnce(() => {
            throw new Error('Failed to read data');
        });

        const licenseObject = LicenseLynx.map('license1');


        expect(licenseObject).toBe(null);
        expect(console.error).toHaveBeenCalled();
    });
});
