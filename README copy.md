# pantheon-docs-reviewer
A specialized GitHub action that summons a Greek pantheon of AI reviewers to analyze documentation PRs, each 'deity' focusing on different aspects of technical writing excellence.

Pantheon-docs-reviewer is a GitHub Action that leverages OpenAI's GPT-4 API to provide intelligent feedback and suggestions on your pull requests. This powerful tool helps improve code quality and saves developers time by automating the code review process.

## Features

- Reviews pull requests using OpenAI's GPT-4 API.
- Provides intelligent comments and suggestions for improving your code.
- Filters out files that match specified exclude patterns.
- Easy to set up and integrate into your GitHub workflow.

## Setup

1. To use this GitHub Action, you need an OpenAI API key. If you don't have one, sign up for an API key
   at [OpenAI](https://beta.openai.com/signup).

2. Add the OpenAI API key as a GitHub Secret in your repository with the name `OPENAI_API_KEY`. You can find more information about GitHub Secrets [here](https://docs.github.com/en/actions/reference/encrypted-secrets).

3. Create a `.github/workflows/main.yml` file in your repository and add the following content: