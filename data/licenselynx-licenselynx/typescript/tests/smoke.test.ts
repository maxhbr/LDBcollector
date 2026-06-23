/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
import { map, Organization } from '../index';

describe('Smoke Integration Tests', () => {
  test('stable map lookup for 0BSD', async () => {
    const result = await map('0BSD');
    expect(result).toBeDefined();
    expect(result.id).toBe('0BSD');
  });

  test('risky map lookup with flag enabled for libpng-2.0', async () => {
    const result = await map('LIbpng License v2', true);
    expect(result).toBeDefined();
    expect(result.id).toBe('libpng-2.0');
  });

  test('risky entry must not resolve without the flag', async () => {
    await expect(map('LIbpng License v2')).rejects.toThrow();
  });

  test('organization-scoped lookup for SISL-1.5', async () => {
    const result = await map('Siemens Inner Source License v1.5', false, Organization.Siemens);
    expect(result).toBeDefined();
    expect(result.id).toBe('SISL-1.5');
    expect(result.src).toBe('siemens');
  });

  test('organization entry must not resolve without the org parameter', async () => {
    await expect(map('Siemens Inner Source License v1.5')).rejects.toThrow();
  });
});
