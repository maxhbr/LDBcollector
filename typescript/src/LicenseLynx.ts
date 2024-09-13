import * as fs from 'fs';

function map(licenseName: string) {
    try {
        const mergedData = JSON.parse(fs.readFileSync('src/resources/merged_data.json', 'utf8'));
        return mergedData[licenseName] || { error: 'License not found' };
    } catch (error) {
        console.error('Error reading data:', error);
        return { error: 'Failed to read data' };
    }
}

export { map };
