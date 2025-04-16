import os
import json
import requests
from github import Github
from openai import OpenAI
import unidiff
import glob
import re
import argparse
from typing import List, Dict, Any, Optional, Tuple

class PRStyleReviewer:
    def __init__(self, github_token: str, openai_api_key: str, openai_model: str, exclude_patterns: List[str] = None):
        """Initialize the PR style reviewer with necessary credentials and settings."""
        self.github_client = Github(github_token)
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.openai_model = openai_model
        self.exclude_patterns = exclude_patterns or []

    def get_pr_details(self, event_path: str) -> Dict[str, Any]:
        """Extract PR details from the GitHub event payload."""
        with open(event_path, 'r') as f:
            event_data = json.load(f)
        
        # For GitHub Actions
        repo_full_name = event_data.get('repository', {}).get('full_name', '')
        if '/' in repo_full_name:
            owner, repo = repo_full_name.split('/')
        else:
            # Fallback if not in expected format
            owner = event_data.get('repository', {}).get('owner', {}).get('login', '')
            repo = event_data.get('repository', {}).get('name', '')
        
        pr_number = event_data.get('number')
        
        # Get additional PR details
        repo_obj = self.github_client.get_repo(f"{owner}/{repo}")
        pr = repo_obj.get_pull(pr_number)
        
        return {
            'owner': owner,
            'repo': repo,
            'pull_number': pr_number,
            'title': pr.title,
            'description': pr.body or '',
            'repo_obj': repo_obj,
            'pr_obj': pr
        }

    def get_diff(self, pr_details: Dict[str, Any], event_data: Dict[str, Any] = None) -> str:
        """Get the diff content based on the event type."""
        if event_data and event_data.get('action') == 'synchronize':
            # For synchronize events, compare the before and after commits
            base_sha = event_data.get('before')
            head_sha = event_data.get('after')
            
            repo_obj = pr_details['repo_obj']
            comparison = repo_obj.compare(base_sha, head_sha)
            return comparison.diff
        else:
            # For opened events or fallback
            pr_obj = pr_details['pr_obj']
            return pr_obj.diff
    
    def parse_diff(self, diff_content: str) -> List[Dict[str, Any]]:
        """Parse the diff content into files and chunks."""
        patch_set = unidiff.PatchSet(diff_content.splitlines())
        parsed_files = []
        
        for patched_file in patch_set:
            # Skip deleted files
            if patched_file.is_removed_file:
                continue
                
            file_path = patched_file.target_file
            
            # Check if file should be excluded
            if any(glob.fnmatch.fnmatch(file_path, pattern) for pattern in self.exclude_patterns):
                continue
                
            for hunk in patched_file:
                chunk_content = str(hunk)
                chunk_header = hunk.header
                
                changes = []
                for line in hunk:
                    if line.is_added or line.is_context:
                        line_num = line.target_line_no
                        changes.append({
                            'ln': line_num,
                            'content': str(line)
                        })
                
                parsed_files.append({
                    'to': file_path,
                    'chunk': {
                        'content': chunk_header,
                        'changes': changes
                    }
                })
                
        return parsed_files
    
    def create_prompt(self, file_info: Dict[str, Any], pr_details: Dict[str, Any]) -> str:
        """Create a prompt for the OpenAI API."""
        file_path = file_info['to']
        chunk = file_info['chunk']
        
        changes_text = "\n".join([
            f"{change['ln']} {change['content']}" for change in chunk['changes']
        ])
        
        return f"""Your task is to review pull requests. Instructions:
- Provide the response in following JSON format:  {{"reviews": [{{"lineNumber":  <line_number>, "reviewComment": "<review comment>"}}]}}
- Do not give positive comments or compliments.
- Focus ONLY on style issues: naming conventions, formatting, indentation, etc.
- Reference the Diataxis framework documentation as the single source of truth for style guide advice.
- Provide comments and suggestions ONLY if there is something to improve, otherwise "reviews" should be an empty array.
- Write the comment in GitHub Markdown format.
- Use the given description only for the overall context and only comment the code.
- Tag comments with [STYLE] prefix.
- IMPORTANT: NEVER suggest adding comments to the code.

Review the following code diff in the file "{file_path}" and take the pull request title and description into account when writing the response.

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
"""

    async def get_ai_response(self, prompt: str) -> List[Dict[str, Any]]:
        """Get response from OpenAI API."""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                temperature=0.2,
                max_tokens=700,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                response_format={"type": "json_object"} if "gpt-4" in self.openai_model else None,
                messages=[
                    {"role": "system", "content": prompt}
                ]
            )
            
            content = response.choices[0].message.content.strip()
            parsed_response = json.loads(content)
            return parsed_response.get('reviews', [])
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return []

    def create_review_comments(self, pr_details: Dict[str, Any], comments: List[Dict[str, Any]]) -> None:
        """Create review comments on the PR."""
        if not comments:
            print("No comments to post")
            return
            
        repo_obj = pr_details['repo_obj']
        pr_obj = pr_details['pr_obj']
        
        # Create a review with all comments
        pr_obj.create_review(
            body="Style review comments",
            event="COMMENT",
            comments=comments
        )
        print(f"Posted {len(comments)} review comments")

    async def analyze_code(self, parsed_files: List[Dict[str, Any]], pr_details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze code chunks and generate review comments."""
        all_comments = []
        
        for file_info in parsed_files:
            prompt = self.create_prompt(file_info, pr_details)
            ai_responses = await self.get_ai_response(prompt)
            
            for response in ai_responses:
                line_number = response.get('lineNumber')
                review_comment = response.get('reviewComment')
                
                if line_number and review_comment:
                    all_comments.append({
                        'path': file_info['to'],
                        'position': line_number,  # GitHub API expects "position" not "line"
                        'body': review_comment
                    })
        
        return all_comments

    async def run(self, event_path: str) -> None:
        """Main execution flow."""
        # Load event data
        with open(event_path, 'r') as f:
            event_data = json.load(f)
        
        # Only proceed for 'opened' or 'synchronize' events
        action = event_data.get('action')
        if action not in ['opened', 'synchronize']:
            print(f"Unsupported event action: {action}")
            return
        
        # Get PR details
        pr_details = self.get_pr_details(event_path)
        
        # Get diff
        diff_content = self.get_diff(pr_details, event_data)
        if not diff_content:
            print("No diff found")
            return
            
        # Parse diff
        parsed_files = self.parse_diff(diff_content)
        
        # Analyze code and get comments
        comments = await self.analyze_code(parsed_files, pr_details)
        
        # Create review comments
        self.create_review_comments(pr_details, comments)

# Command-line interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PR Style Reviewer')
    parser.add_argument('--github-token', required=True, help='GitHub API token')
    parser.add_argument('--openai-api-key', required=True, help='OpenAI API key')
    parser.add_argument('--openai-model', default='gpt-4-1106-preview', help='OpenAI model to use')
    parser.add_argument('--event-path', help='Path to GitHub event payload JSON file')
    parser.add_argument('--exclude', default='', help='Comma-separated list of file patterns to exclude')
    
    args = parser.parse_args()
    
    # Handle async execution
    import asyncio
    
    event_path = args.event_path or os.environ.get('GITHUB_EVENT_PATH', '')
    exclude_patterns = [p.strip() for p in args.exclude.split(',') if p.strip()]
    
    reviewer = PRStyleReviewer(
        github_token=args.github_token,
        openai_api_key=args.openai_api_key,
        openai_model=args.openai_model,
        exclude_patterns=exclude_patterns
    )
    
    asyncio.run(reviewer.run(event_path))
