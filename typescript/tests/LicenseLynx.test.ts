import * as fs from 'fs';
import { map } from '../src/LicenseLynx';

jest.mock('fs', () => ({
  readFileSync: jest.fn(),
}));

describe('map function', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should return data when license exists', () => {
    const mockedData = {
      license1: { some: 'data' },
      license2: { other: 'data' },
    };
    (fs.readFileSync as jest.Mock).mockReturnValueOnce(JSON.stringify(mockedData));

    expect(map('license1')).toEqual({ some: 'data' });
  });

  it('should return error when license not found', () => {
    const mockedData = {
      license1: { some: 'data' },
      license2: { other: 'data' },
    };
    (fs.readFileSync as jest.Mock).mockReturnValueOnce(JSON.stringify(mockedData));

    expect(map('nonexistentLicense')).toEqual({ error: 'License not found' });
  });

  it('should return error when failed to read data', () => {
    (fs.readFileSync as jest.Mock).mockImplementationOnce(() => {
      throw new Error('Failed to read data');
    });

    expect(map('license1')).toEqual({ error: 'Failed to read data' });
  });
});
