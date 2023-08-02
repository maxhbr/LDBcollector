/*
 * SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
 *
 * SPDX-License-Identifier: AGPL-3.0-only
 */

/** @type {import('vite').UserConfig} */
export default {
  root: 'vite_modules/src/hermine',
  base: '/static/',
  build: {
    outDir: '../../dist/hermine'
  },
}