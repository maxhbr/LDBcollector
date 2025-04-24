/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: Apache-2.0
 */
module.exports = {
    transform: {'^.+\\.ts?$': 'ts-jest'},
    testEnvironment: 'node',
    testRegex: '/tests/.*\\.(test|spec)?\\.(ts|tsx)$',
    moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
    moduleNameMapper: {
        "<rootDir>/resources/merged_data.json": "<rootDir>/tests/resources/merged_data.json",
    },
};
