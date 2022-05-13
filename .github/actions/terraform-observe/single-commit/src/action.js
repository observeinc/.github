const core = require('@actions/core');
const github = require('@actions/github');

async function run() {
  try {
    const client = github.getOctokit(process.env.GITHUB_TOKEN);
    const contextPullRequest = github.context.payload.pull_request;
    const {data: pullRequest} = await client.rest.pulls.get({
      owner: contextPullRequest.base.user.login,
      repo: contextPullRequest.base.repo.name,
      pull_number: contextPullRequest.number
    });
    if (pullRequest.commits > 1) {
      throw new Error(
        `There is more than 1 commit on this PR. Please squash your commits.`
      );
    }
  } catch (error) {
    core.setFailed(error.message);
  }
};

run();