// Copyright 2023, Kry10 Limited
// SPDX-License-Identifier: BSD-2-Clause

// Trigger a new binary verification workflow if there is a kernel
// builds artifact in the current workflow.

const fs = require('fs/promises');

const core = require('@actions/core');
const github = require('@actions/github');
const artifact = require('@actions/artifact');

function to_repo_obj(repo_str) {
  const parts = repo_str.split("/");
  if (parts.length != 2) {
    throw new Error(`Invalid repository: ${repo}`);
  }
  return {
    owner: parts[0],
    repo: parts[1],
  };
}

function from_repo_obj(repo_obj) {
  return `${repo_obj.owner}/${repo_obj.repo}`;
}

async function main() {
  try {
    const input = {
      token: core.getInput('token'),
      tag: core.getInput('tag'),
      repo: core.getInput('repository'),
      event: core.getInput('event'),
      artifact: core.getInput('artifact'),
    };

    let do_trigger = false;

    core.startGroup('Check for artifact');
    const tmp = await fs.mkdtemp(`${process.env.RUNNER_TEMP}/artifact-`);

    try {
      await artifact.create().downloadArtifact(input.artifact, tmp);
      do_trigger = true;
    }
    catch (error) {
      console.log(`Artifact not found: ${input.artifact}`);
      console.log('Will not trigger binary verification');
    }

    await fs.rm(tmp, { recursive: true });
    core.endGroup();

    if (do_trigger) {
      core.startGroup('Send trigger');
      try {
        const octokit = github.getOctokit(input.token);

        const repo = github.context.repo;


        await octokit.rest.repos.createDispatchEvent({
          ...to_repo_obj(input.repo),
          event_type: input.event,
          client_payload: {
            repo: from_repo_obj(github.context.repo),
            run_id: github.context.runId,
            tag: input.tag,
          },
        });

        console.log('Trigger sent')
      }
      finally {
        core.endGroup();
      }
    }
  }
  catch (error) {
    core.setFailed(error instanceof Error ? error.message : String(error));
  }
}

main();
