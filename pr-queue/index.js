/*
 * Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
 *
 * SPDX-License-Identifier: BSD-2-Clause
 */

const core = require('@actions/core');
const github = require('@actions/github');

/* Check if the trigger was a PR */
function is_pull_request() {
  const base_key = "GITHUB_BASE_REF";
  return base_key in process.env && process.env[base_key] != "";
}

/* Get the target branch to check for PRs against */
function target_branch() {
  if (is_pull_request()) {
    return process.env.GITHUB_BASE_REF;
  } else {
    return process.env.GITHUB_REF;
  }
}

/* Get the name of the PR branch that triggered the PR */
function pr_branch() {
  if (is_pull_request()) {
    return process.env.GITHUB_HEAD_REF;
  }
}

/* Split the repository name into owner and repository */
function repo_split() {
  const repo = process.env.GITHUB_REPOSITORY;
  const split_index = repo.indexOf('/');
  return [repo.substr(0, split_index), repo.substr(split_index + 1)];
}

/* Get the owner of the repository */
function repo_owner() {
  return repo_split()[0];
}

/* Get the name of the repository */
function repo_name() {
  return repo_split()[1];
}

/* Determine if a PR is ahead of its target */
async function is_ahead(octokit, pr) {
  const comparison = await octokit.repos.compareCommits({
    owner: repo_owner(),
    repo: repo_name(),
    base: pr.base.label,
    head: pr.head.label,
  });

  return comparison.data.status == "ahead";
}

/* Determine if a PR has been approved */
async function is_approved(octokit, pr) {
  if ("pr_queue_approved" in pr) {
    return pr["pr_queue_approved"];
  } else {
    const response = await octokit.pulls.listReviews({
      owner: repo_owner(),
      repo: repo_name(),
      pull_number: pr.number,
    });
    const reviews = response.data;

    const has_approved = review => review.state == "APPROVED";
    const approved = reviews.filter(has_approved).length >= 2;
    pr["pr_queue_approved"] = approved;
    return approved;
  }
}

/* Determine if a PR is passing tests */
async function is_passing(octokit, pr) {
  if ("pr_queue_passing" in pr) {
    return pr["pr_queue_passing"];
  } else {
    const check_list = await octokit.checks.listForRef({
      owner: repo_owner(),
      repo: repo_name(),
      ref: pr.head.sha,
      status: "completed",
    });
    const checks = check_list.data.check_runs;

    const is_success = check => check.conclusion == "success";
    const passing = checks.filter(is_success).length == checks.length;
    pr["pr_queue_passing"] = passing;
    return passing;
  }
}

/* Get the name of the PR creator */
function creator(pr) {
  return pr.user.login;
}

/* Get the names of the PR assignees */
function assignees(pr) {
  return pr.assignees.map(assignee => assignee.login);
}

/* Get the names of the PR reviewers */
function reviewers(pr) {
  return pr.requested_reviewers.map(reviewer => reviewer.login);
}

/*
 * Connect to the GitHub API using the access token.
 */
async function connect() {
  // Get the GitHub access token
  const github_token = core.getInput(
    'github_token',
    { required: true },
  );
  core.setSecret(github_token);

  // Connect to github
  return await github.getOctokit(github_token);
}

/* Find all the PRs to a particular branch */
async function find_prs(octokit, sort, direction) {
  const owner = repo_owner();
  const repo = repo_name();
  const base = target_branch();
  console.log(`Finding pulls for ${owner}/${repo}:${base}`);
  const response = await octokit.pulls.list({
    state: "open",
    owner,
    repo,
    base,
    sort,
    direction,
  });
  return response.data;
}

/* Find the candidate and candidate type for the target branch */
async function find_candidate(octokit) {
  /* Find the least recently created PRs */
  prs = await find_prs(octokit, "created", "asc");

  /* Find a merge candidate */
  console.log(`::group::Looking for merge candidate`);
  for (pr of prs) {
    console.log(`Checking #${pr.number}: ${pr.title}`);
    /* Very explicit short-circuiting here, these operations are
     * expensive */
    if (!await is_ahead(octokit, pr)) {
      continue;
    } else if (!await is_passing(octokit, pr)) {
      continue;
    } else if (!await is_approved(octokit, pr)) {
      continue;
    } else {
      console.log(`Using #${pr.number}: ${pr.title}`);
      console.log(`::endgroup::`);
      return {
        branch: pr.head.label,
        kind: "merge",
        pr,
      }
    }
  }
  console.log(`::endgroup::`);

  /* Find the least-recently updated PRs */
  prs.sort((l, r) => l.updated_at.localeCompare(r.updated_at));

  /* Find a rebase candidate */
  console.log(`::group::Looking for rebase candidate`);
  for (pr of prs) {
    /* Very explicit short-circuiting here, these operations are
     * expensive */
    console.log(`Checking #${pr.number}: ${pr.title}`);
    if (!await is_passing(octokit, pr)) {
      continue;
    } else if (!await is_approved(octokit, pr)) {
      continue;
    } else {
      console.log(`Using #${pr.number}: ${pr.title}`);
      console.log(`::endgroup::`);
      return {
        branch: pr.head.label,
        kind: "rebase",
        pr,
      }
    }
  }
  console.log(`::endgroup::`);

  /* Find a review candidate */
  console.log(`::group::Looking for review candidate`);
  for (pr of prs) {
    /* Very explicit short-circuiting here, these operations are
     * expensive */
    console.log(`Checking #${pr.number}: ${pr.title}`);
    if (!await is_passing(octokit, pr)) {
      continue;
    } else {
      console.log(`Using #${pr.number}: ${pr.title}`);
      console.log(`::endgroup::`);
      return {
        branch: pr.head.label,
        kind: "review",
        pr,
      }
    }
  }
  console.log(`::endgroup::`);

  /* Find a fix candidate */
  console.log(`::group::Looking for fix candidate`);
  for (pr of prs) {
    /* Very explicit short-circuiting here, these operations are
     * expensive */
    console.log(`Checking #${pr.number}: ${pr.title}`);
    console.log(`Using #${pr.number}: ${pr.title}`);
    console.log(`::endgroup::`);
    return {
      branch: pr.head.label,
      kind: "fix",
      pr,
    }
  }
  console.log(`::endgroup::`);

  /* No candidate found */
  console.log(`No candidate found`);
}

async function comment(octokit, pr, body) {
  console.log(`::group::Sending comment to #${pr.number}: ${pr.title}`);
  console.log(`${body}`);
  console.log(`::endgroup::`);

  await octokit.issues.createComment({
    owner: repo_owner(),
    repo: repo_name(),
    issue_number: pr.number,
    body,
  })
}

/* Notify a PR that it can be merged */
async function merge_candiate(octokit, pr) {
  var body = assignees(pr).map(user => "@" + user).join(", ");

  if (body != '') {
    body += "\n\n";
  }

  body += "This PR can now be merged via BitBucket.";

  // Notify the assignees
  await comment(octokit, pr, body);

  // Update the PR in bitbucket
  await comment(octokit, pr, "@ssrg-bamboo `test`");
}

/* Notify a PR that it can be rebased to be merged next */
async function rebase_candiate(octokit, pr) {
  var body = `@${creator(pr)}\n\n`;

  body += "This PR must be rebased against the target branch.";

  // Notify the owner
  await comment(octokit, pr, body);
}

/* Notify a PR that it can be reviewed to be merged next */
async function review_candiate(octokit, pr) {
  var body = reviewers(pr).map(user => "@" + user).join(", ");

  if (body != '') {
    body += "\n\n";
  }

  body += "This PR can now be reviewed to be the next to get merged. ";
  body += "Make sure there are at least 2 approvals before merging.";

  // Notify the reviewers
  await comment(octokit, pr, body);
}

/* Notify a PR that it can be fixed to be reviewed next */
async function fix_candiate(octokit, pr) {
  var body = `@${creator(pr)}\n\n`;

  body += "Please ensure the tests on this PR are passing, ";
  body += "once they are, this can be the next PR to be merged.";

  // Notify the owner
  await comment(octokit, pr, body);
}

async function run() {
  const octokit = await connect();

  candidate = await find_candidate(octokit);

  /* Only if triggered by push to target or if the PR would be the
   * target */
  if (candidate !== undefined) {
    console.log(`Selecting candidate: ${candidate.pr.url}`);
    switch (candidate.kind) {
      case "merge":
        await merge_candiate(octokit, candidate.pr);
        break;
      case "rebase":
        await rebase_candiate(octokit, candidate.pr);
        break;
      case "review":
        await review_candiate(octokit, candidate.pr);
        break;
      case "fix":
        await fix_candiate(octokit, candidate.pr);
        break;
    }
  }
}

process.on("unhandledRejection", (reason, promise) => {
  throw reason;
});

run()
