
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

## Extending and Extrapolating

To add new deity reviewers or modify existing ones:
1. Define a new AssistantAgent with appropriate system message
2. Add the agent to the reviewer_agents list
3. Deploy the updated workflow

This is essentially a model for a group of collaborating AI personae.
You could make this model be anything you want it to be: a group of personal advisors, a book editorial staff, or a think tank.

## Troubleshooting

- **No comments appearing**: Check your repository's Action logs for execution details
- **API rate limits**: Ensure your OpenAI API key has sufficient quota
- **Permissions**: Make sure the GitHub token has permission to comment on PRs

## License

This project is available under the MIT License.