# AI Divine Pantheon PR Reviewer

This GitHub Action combines the power of specialized AI reviewers with GitHub's PR review capabilities.

Each "deity" AI reviewer specializes in a different aspect of technical writing quality and provides tailored feedback directly on your pull requests.

The intended audience for this particular pantheon is those focused on improving documentation quality such as:
technical writers, developer advocates, and information architects.

Using this project's structure, you could modify it to become a team of any type focused on doing anything.

![pantheon deities](/img/pantheon_deities.png)

## Features

- **Specialized Review Domains**: Each deity AI reviewer analyzes and generates feedback on various aspects of the technical writing quality in your PR.

- **In-line PR Comments**: Each reviewer's feedback is added as in-line comments at the relevant locations in your PR.

- **General PR Comments**: Each reviewer's feedback is added as general comments on the PR.

## Setup Instructions

### 1. Add the workflow file

Create a file `.github/workflows/pantheon_workflow.yml` in your repository with the content from the provided workflow YAML.

### 2. Add the pantheon reviewer script

Save the provided Python script as `pantheon_pr_reviewer.py` in your repository.

### 3. Set up secrets

Add the following secrets to your GitHub repository:
- `OPENAI_API_KEY`: Your OpenAI API key

### 4. Customize (optional)

You can customize each deity's review behavior by modifying the respective agent definitions in the Python script.

- Adjust each deity's system message to focus on aspects relevant to your codebase
- Add or remove deity reviewers based on your needs
- Modify comment formatting or content focus

Example definition:

```py
# 1. Style Guide Adherence - Apollo (God of Light, Music, and Poetry)
apollo = AssistantAgent(
    "Apollo",
    model_client=model_client,
    system_message="""You are Apollo, God of Light, Music, and Poetry, who serves as the Style Guide Adherence reviewer.
    
    Your divine attributes:
    - Master of harmony, poetry, and artistic expression
    - Patron of the Muses and upholder of aesthetic excellence
    - Possessor of the oracle's vision to see what others cannot

    As Apollo, you speak with refined elegance and poetic precision. You are exacting but not harsh, always seeking the highest standard of written expression. You occasionally reference your talents in music or poetry when making analogies about writing style.

    Your sacred duty is to review technical writing for adherence to organizational style standards, focusing on:
    - Consistency in tone, voice, and perspective (first/second/third person)
    - Proper punctuation and grammatical conventions
    - Appropriate levels of formality
    - Adherence to established style guide conventions    
    - Consistency in naming conventions and code organization
    - Proper indentation and formatting

    When you find inconsistencies, specify the file and line number, quote the problematic content, 
    explain the specific style guideline being violated, and offer corrected alternatives that 
    maintain the original meaning while following the style guide.

    End your reviews with a lyrical statement that summarizes the document's stylistic merits, 
    such as "The harmony of your prose resonates well, though a few discordant notes require tuning."

    Finally, at the bottom of your review, score the code quality on a scale of 0-100, where 100 is perfect adherence to style guidelines.
    Assume high standards for production code. Output the score in the following format: "SCORE: [0-100]". 
    """
)
```

## Usage

The action will automatically run on new pull requests and when pull requests are updated.

You can also manually trigger a review on any PR by:

1. Going to the "Actions" tab in your repository
2. Selecting the "Divine Pantheon Code Review" workflow
3. Clicking "Run workflow"
4. Entering the PR number you want to review

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

## Divine Review Council Behavior

The framework that controls the AI group behavior is [autogen](https://microsoft.github.io/autogen/stable/index.html)

In this implementation, there is only one round of tasks sent to each deity before their respective comments are processed and posted to your PR.

Feel free to explore the [autogen docs](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html) to learn more about how you could customize the AI team's behavior.

The following code within the python script is what configures the AI group's behavior.

```py
        # Define a termination condition that stops the task if a special phrase is mentioned
        text_termination = TextMentionTermination("DOCUMENTATION REVIEW COMPLETE")

        # Create a team with all the Greek gods and goddesses
        greek_pantheon_team = RoundRobinGroupChat(
            [apollo, hermes, athena, hestia, mnemosyne, hephaestus, heracles, demeter, aphrodite, iris, dionysus, chronos, atropos], 
            termination_condition=text_termination
        )

        # Create the task for each deity to perform
        task = f"""Your task is to review the following changes from pull requests according to your divine domain of expertise. Instructions:
        - Respond in the following JSON format:
        {{
        "inlineReviews": [
            {{
            "filename": "{file_path}",
            "position": <position>,  // This is the line number in the unified diff view (starts at 1)
            "reviewComment": "[ReviewType] Poignant and actionable line-specific feedback. Brief reasoning."
            }}
        ],
        "generalReviews": [
            {{
            "filename": "{file_path}",
            "reviewComment": "Respective personality-based summary of content review. SCORE: [0-100] "
            }}
        ]
        }}
        - The `position` is NOT the original file line number.
        - The `position` is the line index (1-based) within the diff block itself.
        - Create a reasonable amount of inlineReview comments (in the JSON format above) as necessary to improve the content without overwhelming the original author who will review the comments.
        - Create one general summary comment reflective of your divine personality that summarized the overall content review (in the JSON format above).
        - Do NOT wrap the output in triple backticks. DO NOT use markdown formatting like ```json.
        - Do NOT include explanations or extra commentary.
        - All comments should reflect your unique personality and domain.
        - Do NOT give positive comments or compliments.
        - Write the comment in GitHub Markdown format.
        - IMPORTANT: NEVER suggest adding comments to the code.

        Review the following code diff in the file "{file_path}".

        Pull request title: {pr_details['title']}
        Pull request description:

        ---
        {pr_details['description']}
        ---

        Git diff to review:

        ```diff
        {chunk['content']}
        {changes_text}
        ```

        Your feedback should be specific, constructive, and actionable.
        """

        # Initialize review collections
        inline_reviews = []
        general_reviews = []

        # Run the review
        print(f"Starting review process with divine pantheon for {file_path}...")
        divine_responses = await greek_pantheon_team.run(task=task)
```

## Extending

To add new deity reviewers or modify existing ones:

1. Define a new AssistantAgent with appropriate system message
2. Add the agent to the `reviewer_agents` list
3. Deploy the updated workflow

To use specific or additional models types (like Gemini or Anthropic):

1. Check out the [autogen docs](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/models.html).
2. Modify this section of the python script:

```py
###################################
# AutoGen model client definitions
###################################

# Create an OpenAI model client
model_client = OpenAIChatCompletionClient(
    model=openai_model,
)
```

It is possible to have multiple models and assign each deity different models.

## Troubleshooting

- **No comments appearing**: Check your repository's Action logs for execution details
- **API rate limits**: Ensure your OpenAI API key has sufficient quota
- **Permissions**: Make sure the GitHub token has permission to comment on PRs

## License

This project is available under the MIT License.
