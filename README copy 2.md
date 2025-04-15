
# Divine Pantheon GitHub PR Reviewer

This GitHub Action combines the power of an autogen "pantheon" of specialized AI reviewers with GitHub's PR review capabilities. Each "deity" reviewer specializes in a different aspect of code quality and provides tailored feedback directly on your pull requests.

## Features

- **Specialized Review Domains**: Each AI reviewer (deity) focuses on a specific aspect of code quality:
  - **Apollo**: Style guide adherence and code aesthetics
  - **Hermes**: Readability and communication clarity
  - **Athena**: Cognitive load reduction and code complexity
  - **Hestia**: Documentation structure and organization
  - **Mnemosyne**: Context completeness
  - **Hephaestus**: Code accuracy and functionality
  - **Heracles**: Cross-linking and code relationships
  - **Demeter**: Terminology consistency
  - **Aphrodite**: Code formatting and visual presentation
  - **Iris**: Accessibility
  - **Dionysus**: Visual aid suggestions
  - **Chronos**: Knowledge decay and outdated patterns

- **Harmonious Summary**: Harmonia provides an integrated review summary combining all feedback

- **In-line PR Comments**: Each reviewer's feedback is added as in-line comments at the relevant locations in your code

## Setup Instructions

### 1. Add the workflow file

Create a file `.github/workflows/pantheon-review.yml` in your repository with the content from the provided workflow YAML.

### 2. Add the pantheon reviewer script

Save the provided Python script as `pantheon_pr_reviewer.py` in your repository.

### 3. Set up secrets

Add the following secrets to your GitHub repository:
- `OPENAI_API_KEY`: Your OpenAI API key

### 4. Configure (optional)

You can customize the pantheon reviewers by modifying the Python script:
- Adjust each deity's system message to focus on aspects relevant to your codebase
- Add or remove deity reviewers based on your needs
- Modify comment formatting or content focus

## Usage

The action will automatically run on new pull requests and when pull requests are updated.

You can also manually trigger a review on any PR by:
1. Going to the "Actions" tab in your repository
2. Selecting the "Divine Pantheon Code Review" workflow
3. Clicking "Run workflow"
4. Entering the PR number you want to review

## Example Output

Each review comment will be tagged with the deity name and domain:

```
### [Apollo - Style Guide Adherence]

Line 42 violates the project's naming convention. 
The variable `tmp_var` should follow camelCase: `tmpVar`
```

## Extending

To add new deity reviewers or modify existing ones:
1. Define a new AssistantAgent with appropriate system message
2. Add the agent to the reviewer_agents list
3. Deploy the updated workflow

## Troubleshooting

- **No comments appearing**: Check your repository's Action logs for execution details
- **API rate limits**: Ensure your OpenAI API key has sufficient quota
- **Permissions**: Make sure the GitHub token has permission to comment on PRs

## License

This project is available under the MIT License.



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

```yaml
name: AI Code Reviewer

on:
  pull_request:
    types:
      - opened
      - synchronize
permissions: write-all
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repo
        uses: actions/checkout@v4

      - name: AI Code Reviewer
        uses: your-username/pantheon-docs-reviewer@main
        with:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }} # The GITHUB_TOKEN is there by default so you just need to keep it like it is and not necessarily need to add it as secret as it will throw an error. [More Details](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#about-the-github_token-secret)
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          OPENAI_API_MODEL: "gpt-4" # Optional: defaults to "gpt-4"
          exclude: "**/*.json, **/*.md" # Optional: exclude patterns separated by commas
```

4. Replace `your-username` with your GitHub username or organization name where the AI Code Reviewer repository is
   located.

5. Customize the `exclude` input if you want to ignore certain file patterns from being reviewed.

6. Commit the changes to your repository, and AI Code Reviewer will start working on your future pull requests.

## How It Works

The AI Code Reviewer GitHub Action retrieves the pull request diff, filters out excluded files, and sends code chunks to the OpenAI API. It then generates review comments based on the AI's response and adds them to the pull request.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests to improve the AI Code Reviewer GitHub Action.

Let the maintainer generate the final package (`yarn build` & `yarn package`).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
