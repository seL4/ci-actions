/*
 * Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
 *
 * SPDX-License-Identifier: BSD-2-Clause
 */

import { dirname } from 'path';
import { fileURLToPath } from 'url';
import { addPath, getInput, setFailed } from '@actions/core';
import { exec } from '@actions/exec';

export async function run(steps) {
  const action_name = getInput('action_name');
  try {
    const src_dir = dirname(fileURLToPath(import.meta.url));
    const script_dir = `${src_dir}/../scripts`;
    addPath(script_dir);
    const options = { };
    options.env = process.env;
    options.env.SCRIPTS = `${script_dir}`;
    addPath(process.env.HOME + '/.local/bin')
    const action_dir = `${src_dir}/../${action_name}`
    await exec(`${action_dir}/${steps}`, [], options);
  } catch (error) {
    setFailed(`Action ${action_name} failed.`);
  }
}
