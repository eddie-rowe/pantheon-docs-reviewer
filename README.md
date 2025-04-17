# AI Divine Pantheon PR Reviewer

This GitHub Action combines the power of specialized AI reviewers with GitHub's PR review capabilities.

Each "deity" reviewer specializes in a different aspect of technical writing quality and provides tailored feedback directly on your pull requests.

The intended audience for this particular pantheon is those focused on improving documentation quality: technical writers, developer advocates, and information architects.

![pantheon deities](/img/pantheon_deities.png)

## Features

- **Specialized Review Domains**: Each AI reviewer (deity) focuses on a specific aspect of code quality:
  - **Apollo**: Style guide adherence
  - **Hermes**: Readability and communication clarity
  - **Athena**: Cognitive load reduction
  - **Hestia**: Documentation structure and organization
  - **Mnemosyne**: Context completeness
  - **Hephaestus**: Code accuracy and functionality
  - **Heracles**: Cross-linking opportunities
  - **Demeter**: Terminology consistency
  - **Aphrodite**: Formatting and beauty
  - **Iris**: Accessibility
  - **Dionysus**: Visual aid enhancements
  - **Chronos**: Knowledge decay and outdated patterns

- **Atropos**: Atropos ensures all deities have responded and ends the review.

- **In-line PR Comments**: Each reviewer's feedback is added as in-line comments at the relevant locations in your code

- **General PR Comments**: Each reviewer's feedback is added as in-line comments at the relevant locations in your code

## Setup Instructions

1. Add the workflow file

Create a file `.github/workflows/pantheon-review.yml` in your repository with the content from the provided workflow YAML.

1. Add the pantheon reviewer script

Save the provided Python script as `pantheon_pr_reviewer.py` in your repository.

1. Set up secrets

Add the following secrets to your GitHub repository:
- `OPENAI_API_KEY`: Your OpenAI API key

1. Configure (optional)

You can customize the pantheon reviewers by modifying the Python script:

- Adjust each deity's system message to focus on aspects relevant to your codebase
- Add or remove deity reviewers based on your needs
- Modify comment formatting or content focus

## Usage

The action will automatically run on new pull requests and when pull requests are updated.

You can also manually trigger a review on any PR by:

1. Going to the "Actions" tab in your repository
1. Selecting the "Divine Pantheon Code Review" workflow
1. Clicking "Run workflow"
1. Entering the PR number you want to review

## Example Output

### In-line review

Each deity will leave a reasonable number of in-line reviews.

```txt
Apollo: [Structure] The new section '## Extending' is introduced without proper context. 
Consider adding a sentence that links this section to the previous content, thereby emphasizing its relevance.
```

### General review

Each deity will leave a single general review.

```txt
Hestia's Review of README.md
The foundation of this document is built with intention, yet it requires further reinforcement. 
Enhancing the clarity and specificity of your instructions will ensure a solid structure for all who seek guidance. 
SCORE: 65
```

## Extending

To add new deity reviewers or modify existing ones:

1. Define a new AssistantAgent with appropriate system message
1. Add the agent to the reviewer_agents list
1. Deploy the updated workflow

This project could be modified to be a team of anything set on doing anything.

## Troubleshooting

- **No comments appearing**: Check your repository's Action logs for execution details
- **API rate limits**: Ensure your OpenAI API key has sufficient quota
- **Permissions**: Make sure the GitHub token has permission to comment on PRs

## License

This project is available under the MIT License.