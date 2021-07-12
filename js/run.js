/*
 * Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
 *
 * SPDX-License-Identifier: BSD-2-Clause
 */

const core = require('@actions/core');
const exec = require('@actions/exec');

module.exports = {
  run: async function(steps) {
    const action_name = core.getInput('action_name');
    try {
      const src_dir = __dirname;
      const script_dir = `${src_dir}/../scripts`;
      core.addPath(script_dir);
      const options = { };
      options.env = process.env;
      options.env.SCRIPTS = `${script_dir}`;
      core.addPath(process.env.HOME + '/.local/bin')
      const action_dir = `${src_dir}/../${action_name}`
      await exec.exec(`${action_dir}/${steps}`, [], options);
    } catch (error) {
      core.setFailed(`Action ${action_name} failed.`);
    }
  }
}
