// Copyright 2023, Kry10 Limited
// SPDX-License-Identifier: BSD-2-Clause

// Wait for artifacts to become available in another workflow run,
// and optionally download them.

// Currently makes no attempt to handle GitHub API rate limits.
// Downloads might only work for modest artifact file sizes, since
// downloadArtifact slurps each whole artifact into memory before
// writing it to the filesystem.

const fs = require('fs/promises');

const core = require('@actions/core');
const github = require('@actions/github');
const exec = require('@actions/exec')

async function main() {
  try {
    const repo_full = core.getInput("repo");
    const repo_parts = repo_full.split("/");

    if (repo_parts.length !== 2) {
      throw new Error(`Invalid repository: ${repo_full}`);
    }

    const repo = {
      owner: repo_parts[0],
      repo: repo_parts[1],
    };

    const run_id = core.getInput('run-id');
    const artifact_names = core.getInput('artifact-names').trim().split(/\s+/);

    const download_dir = core.getInput('download-dir');
    if (download_dir) {
      await fs.mkdir(download_dir, {recursive: true});
    }

    const timeout = parseInt(core.getInput('timeout'), 10);
    const token = core.getInput('token');

    const octokit = github.getOctokit(token);

    const artifacts = await workflow_artifacts({
      repo, run_id, artifact_names, download_dir, timeout, octokit
    });

    const artifact_ids = artifact_names.map(name => artifacts.get(name).id);
    core.setOutput('artifact-ids', artifact_ids.join(" "));
  }
  catch (error) {
    core.setFailed(error.message);
  }
}

// Wait up to a timeout for named artifacts to become available in another workflow.
// If a `download_dir` is provided, download artifact files to that directory.
// Return artifact resources, as a Map from artifact name to artifact object.
async function workflow_artifacts({repo, run_id, artifact_names, download_dir, timeout, octokit}) {
  // Names of artifacts we're still waiting for.
  const waiting = new Set(artifact_names);

  // Artifacts we've found so far.
  // Map from artifact names to full artifact resources.
  const found = new Map();

  // Track files we still need to download.
  // Serialise downloads to avoid concurrent API requests.
  let to_download = [];

  const download_tmp = await fs.mkdtemp(`${process.env.RUNNER_TEMP}/artifacts-`);

  async function download_pending_real() {
    while (to_download.length > 0) {
      const artifact_name = to_download.shift();
      const artifact = found.get(artifact_name);
      console.log(`Downloading ${artifact_name}`);
      const download = await octokit.rest.actions.downloadArtifact({
        ...repo, artifact_id: artifact.id, archive_format: 'zip'
      });
      const zip_name = `${download_tmp}/${artifact_name}.zip`;
      const dir_name = `${download_dir}/${artifact_name}`;
      try {
        await fs.writeFile(zip_name, Buffer.from(download.data));
        console.log(`Unpacking ${artifact_name}`);
        const unzip_rc = await exec.exec('unzip', ['-d', dir_name, zip_name]);
        if (unzip_rc !== 0) {
          throw new Error(`Failed to unpack ${artifact_name}`);
        }
        console.log(`Unpacked ${artifact_name} to ${dir_name}`);
      }
      finally {
        await fs.rm(zip_name, { force: true });
      }
    }
  }

  async function download_pending_dummy() {
    to_download = [];
  }

  const download_pending = download_dir ? download_pending_real : download_pending_dummy;

  try {
    // We keep trying until the timeout, then try once more.
    const time_to_give_up = Date.now() + timeout * 1000;
    let try_again = true;

    while (try_again) {
      console.log(`Waiting for artifacts: ${[...waiting].join(" ")}`);

      // Allow one more try past the timeout.
      if (Date.now() > time_to_give_up) {
        try_again = false;
      }

      // Artifact results might come in multiple pages, so we iterate.
      const artifact_iterator = octokit.paginate.iterator(
        octokit.rest.actions.listWorkflowRunArtifacts,
        { ...repo, run_id, per_page: 100 },
      );

      // On each attempt, first work through all the artifact result pages.
      for await (const {data} of artifact_iterator) {
        for (const artifact of data) {
          if (waiting.has(artifact.name)) {
            console.log(`Found ${artifact.name}`);
            waiting.delete(artifact.name);
            found.set(artifact.name, artifact);
            to_download.push(artifact.name);
          }
        }
        // Return as soon as we have found everything we need.
        if (waiting.size === 0) {
          await download_pending();
          return found;
        }
      }

      // Download any artifacts we've found so far, then try again.
      await download_pending();
      await new Promise(resolve => setTimeout(resolve, 10000));
    }
    throw new Error("Expected artifacts not found");
  }

  finally {
    await fs.rm(download_tmp, { recursive: true });
  }

}

main();
