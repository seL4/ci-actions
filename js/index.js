/*
 * Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
 *
 * SPDX-License-Identifier: BSD-2-Clause
 */

const core = require('@actions/core');
const exec = require('@actions/exec');

const run = async function() {
  try {
    const src_dir = __dirname;
    const script_dir = `${src_dir}/../scripts`;
    const action_name = core.getInput('action_name');
    const action_dir = `${src_dir}/../${action_name}`
    const options = { };
    options.env = process.env;
    options.env.SCRIPTS = `${script_dir}`;
    await exec.exec(`${action_dir}/steps.sh`, [], options);
  } catch (error) {
    core.setFailed(error.message);
  }
}

run();