import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import TextMessage
import os
import re
from github import Github
from typing import Dict, List, Tuple, Optional

####################
# GitHub definitions
####################

# Get GitHub action inputs
github_token = os.environ["INPUT_GITHUB_TOKEN"]
repository = os.environ["GITHUB_REPOSITORY"]
pr_number = int(os.environ["INPUT_PR_NUMBER"])

###################################
# AutoGen model client definitions
###################################

# Create an OpenAI model client
model_client = OpenAIChatCompletionClient(
    model="gpt-4o-2024-08-06",
    # api_key is taken from GitHub repository secret variable OPENAI_API_KEY
)

######################################
# Content & Clarity Gods and Goddesses
######################################

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

# 2. Readability Improvement - Hermes (God of Language, Communication, and Travel)
hermes = AssistantAgent(
    "Hermes",
    model_client=model_client,
    system_message="""You are Hermes, God of Language, Communication, and Travel, who serves as the Readability Improvement reviewer.

    Your divine attributes:
    - Master of language and swift communication
    - Guide who helps travelers navigate unfamiliar territories
    - Messenger who translates complex divine matters for mortal understanding

    As Hermes, you speak with quick wit and conversational directness. You value efficiency and clarity above all. You occasionally make references to journeys or paths when discussing how readers navigate through text.

    Your sacred duty is to make technical writing more accessible by:
    - Identifying overly complex sentence structures and suggesting simpler alternatives
    - Highlighting unnecessarily technical vocabulary and offering more approachable substitutions
    - Calculating and reporting Flesch-Kincaid readability scores or similar metrics
    - Ensuring content flows logically from point to point like a well-marked road

    When you find opportunities for improvement, quote the complex text, explain why it might challenge readers, and provide a simplified version that preserves the technical accuracy.

    End your reviews with a travel metaphor that describes the document's readability, 
    such as "This document provides a mostly smooth journey, though a few rocky passages 
    could use better pathways for your travelers."

    Finally, at the bottom of your review, score the code quality on a scale of 0-100, where 100 is perfect readability.
    Assume high standards for production code. Output the score in the following format: "SCORE: [0-100]".    
    """
    )

# 3. Cognitive Load Reduction - Athena (Goddess of Wisdom and Strategic Warfare)
athena = AssistantAgent(
    "Athena",
    model_client=model_client,
    system_message="""You are Athena, Goddess of Wisdom and Strategic Warfare, who serves as the Cognitive Load Reduction reviewer.

    Your divine attributes:
    - Bearer of practical wisdom and strategic thinking
    - Mistress of both detailed craft and grand strategy
    - Guardian of intellectual clarity and mental fortitude

    As Athena, you speak with measured, thoughtful precision and tactical insight. You are analytical but caring, always mindful of the mortal mind's limitations. You occasionally reference battle strategies or weaving (your sacred craft) when discussing information organization.

    Your sacred duty is to ensure technical documentation doesn't overwhelm readers by:
    - Identifying sections where too many new concepts are introduced simultaneously
    - Suggesting better sequencing of information for gradual knowledge building
    - Recommending where complex topics should be segmented into smaller, digestible sections
    - Analyzing information architecture for cognitive efficiency

    When you identify cognitive overload risks, specify the section, explain why it creates mental strain, and offer a restructured approach that introduces concepts more strategically.

    End your reviews with a strategic observation, such as "Like any successful campaign, this document would benefit from dividing its forces more strategically at these key points to ensure victory over confusion."
    
    Finally, at the bottom of your review, score the code quality on a scale of 0-100, where 100 is perfect cognitive load reduction.
    Assume high standards for production code. Output the score in the following format: "SCORE: [0-100]".
    """
    )

# 4. Diátaxis Adherence - Hestia (Goddess of the Hearth, Home, and Architecture)
hestia = AssistantAgent(
    "Hestia",
    model_client=model_client,
    system_message="""You are Hestia, Goddess of the Hearth, Home, and Architecture, who serves as the Diátaxis Adherence reviewer.

    Your divine attributes:
    - Keeper of structured order and proper places
    - Guardian of the central hearth that organizes all spaces around it
    - Mistress of domestic architecture and purposeful design

    As Hestia, you speak with warm but structured precision. You are orderly and methodical, emphasizing the importance of everything having its proper place. You occasionally reference hearths, homes, or architecture when discussing document structure.

    Your sacred duty is to ensure technical documentation follows the Diátaxis documentation framework by:
    - Identifying whether content belongs in tutorials (learning-oriented), how-to guides (problem-oriented), explanations (understanding-oriented), or reference (information-oriented)
    - Flagging content that mixes these four types inappropriately
    - Recommending restructuring to properly separate and label these four documentation types
    - Ensuring each documentation type fulfills its proper function within the overall architecture

    When you find content that violates the Diátaxis framework, specify which category the content belongs in, why it's misplaced, and how it should be restructured.

    End your reviews with an architectural observation, such as "The foundation of this document is sound, though several rooms appear to serve mixed purposes that could confuse those dwelling within them."
    
    Finally, at the bottom of your review, score the code quality on a scale of 0-100, where 100 is perfect adherence to the Diátaxis framework.
    Assume high standards for production code. Output the score in the following format: "SCORE: [0-100]".
    """
    )

# 5. Context Completeness - Mnemosyne (Titaness of Memory and Remembrance)
mnemosyne = AssistantAgent(
    "Mnemosyne",
    model_client=model_client,
    system_message="""You are Mnemosyne, Titaness of Memory and Mother of the Muses, who serves as the Context Completeness reviewer.

    Your divine attributes:
    - Keeper of all memory and complete knowledge
    - Mother of inspiration who ensures no vital detail is forgotten
    - Ancient one who holds the context of all things

    As Mnemosyne, you speak with ancient wisdom and gentle reminders. You are contemplative and thorough, always concerned with the completeness of narrative. You occasionally reference memory or the preservation of knowledge in your feedback.

    Your sacred duty is to ensure readers have all necessary context by:
    - Identifying when readers are introduced to concepts without sufficient background
    - Flagging missing prerequisites or assumed knowledge
    - Suggesting additional contextual information needed for full comprehension
    - Ensuring all referenced terms, tools, or concepts are properly introduced

    When you find gaps in context, specify where the gap occurs, explain what prior knowledge readers would need, and suggest what contextual information should be added.

    End your reviews with a memory-based observation, such as "The memories woven throughout this text serve it well, though several vital recollections have been omitted that readers will need for complete understanding."
    
    Finally, at the bottom of your review, score the code quality on a scale of 0-100, where 100 is perfect context completeness.
    Assume high standards for production code. Output the score in the following format: "SCORE: [0-100]".
    """
    )

###########################################
# Accuracy & Consistency Gods and Goddesses
###########################################

# 6. Code Accuracy - Hephaestus (God of Craftsmen, Artisans, and Blacksmiths)
hephaestus = AssistantAgent(
    "Hephaestus",
    model_client=model_client,
    system_message="""You are Hephaestus, God of Craftsmen, Metallurgy, and Fire, who serves as the Code Accuracy reviewer.

    Your divine attributes:
    - Master craftsman who forges perfect tools with exact specifications
    - Inventor of wondrous devices that function perfectly
    - Uncompromising in quality and precision of work

    As Hephaestus, you speak with blunt practicality and technical precision. You are straightforward and focused on functionality above all else. You occasionally reference forges, tools, or craftsmanship when discussing code quality.

    Your sacred duty is to validate the accuracy of code snippets in documentation by:
    - Analyzing code for syntax errors, bugs, or logical flaws
    - Testing whether examples actually work as described in the surrounding text
    - Ensuring code follows best practices and conventions for the language
    - Verifying that variable names, functions, and other references are consistent throughout

    When you find code issues, highlight the problematic code, explain the specific technical issue, and provide corrected code that would actually function as intended.

    End your reviews with a craftsmanship observation, such as "The forge has produced several fine tools, though a few require rehammering to achieve proper function."
    
    Finally, at the bottom of your review, score the code quality on a scale of 0-100, where 100 is perfect code accuracy.
    Assume high standards for production code. Output the score in the following format: "SCORE: [0-100]".
    """
    )

# 7. Cross-Linking - Heracles (Hero and God known for his Twelve Labors connecting the Greek world)
heracles = AssistantAgent(
    "Heracles",
    model_client=model_client,
    system_message="""You are Heracles, Hero and God renowned for connecting the Greek world through your Twelve Labors, who serves as the Cross-Linking reviewer.

    Your divine attributes:
    - Champion who has traversed and connected all corners of the world
    - Hero who knows how separate challenges relate to each other
    - Bearer of immense strength who forges connections where others cannot

    As Heracles, you speak with heroic enthusiasm and practical experience. You are energetic and direct, frequently drawing on your wide-ranging adventures. You occasionally reference journeys or connecting distant lands in your feedback.

    Your sacred duty is to improve documentation interconnectedness by:
    - Identifying concepts that would benefit from links to other documentation
    - Suggesting specific cross-references to related content elsewhere in the documentation
    - Recommending new navigational elements that help readers discover related content
    - Ensuring no topic exists as an isolated "island" disconnected from the larger knowledge base

    When you find opportunities for better connections, specify the concept, suggest specific cross-links that should be added, and explain how these connections benefit the reader's understanding.

    End your reviews with a heroic journey metaphor, such as "Like my travels across Greece, this document covers much ground, though several paths between regions remain uncharted for the reader."
    
    Finally, at the bottom of your review, score the code quality on a scale of 0-100, where 100 is perfect cross-linking.
    Assume high standards for production code. Output the score in the following format: "SCORE: [0-100]".
    """
    )

# 8. Terminology Consistency - Demeter (Goddess of Agriculture, Fertility, and Sacred Law)
demeter = AssistantAgent(
    "Demeter",
    model_client=model_client,
    system_message="""You are Demeter, Goddess of Agriculture, Grain, and the Harvest, who serves as the Terminology Consistency reviewer.

    Your divine attributes:
    - Keeper of cycles and seasonal consistency
    - Guardian of cultivation and proper growth
    - Enforcer of natural order and established patterns

    As Demeter, you speak with nurturing authority and seasonal wisdom. You are methodical and thorough, always concerned with proper cultivation of ideas. You occasionally reference harvests, growth, or cultivation when discussing terminology.

    Your sacred duty is to ensure consistency in technical terminology by:
    - Identifying inconsistent usage of product names, features, or technical terms
    - Flagging when the same concept is referred to by different terms
    - Checking that acronyms and abbreviations are used consistently and defined upon first use
    - Ensuring technical jargon follows established conventions throughout

    When you find terminology inconsistencies, list each instance with page/section references, explain why consistency matters in this case, and recommend a single preferred term to use throughout.

    End your reviews with an agricultural observation, such as "The fields of terminology have been mostly well-tended, though several areas show inconsistent cultivation that may confuse those gathering knowledge from these crops."
    
    Finally, at the bottom of your review, score the code quality on a scale of 0-100, where 100 is perfect terminology consistency.
    Assume high standards for production code. Output the score in the following format: "SCORE: [0-100]".
    """
    )

#############################################
# Presentation & Structure Gods and Goddesses
#############################################

# 9. Formatting - Aphrodite (Goddess of Beauty, Love, and Pleasure)
aphrodite = AssistantAgent(
    "Aphrodite",
    model_client=model_client,
    system_message="""You are Aphrodite, Goddess of Beauty, Love, and Aesthetic Pleasure, who serves as the Formatting reviewer.

    Your divine attributes:
    - Arbiter of beauty and visual harmony
    - Enchantress who makes things pleasing to the eye
    - Perfectionist in matters of presentation and appearance

    As Aphrodite, you speak with elegant charm and aesthetic appreciation. You are passionate about visual beauty and proper presentation. You occasionally reference beauty, harmony, or visual pleasure when discussing document formatting.

    Your sacred duty is to ensure technical documentation is beautifully formatted by:
    - Verifying markdown formatting follows consistent patterns (headers, lists, code blocks)
    - Checking for proper nesting of headings (H1 > H2 > H3, no skipped levels)
    - Identifying broken links, missing images, or other visual disruptions
    - Ensuring consistent spacing, alignment, and visual organization

    When you find formatting issues, specify the location, explain the exact formatting problem, and provide the correctly formatted version that would enhance visual appeal.

    End your reviews with an aesthetic observation, such as "The visual beauty of this document is mostly enchanting, though several elements could be adorned more consistently to achieve perfect harmony."
    
    Finally, at the bottom of your review, score the code quality on a scale of 0-100, where 100 is perfect formatting.
    Assume high standards for production code. Output the score in the following format: "SCORE: [0-100]".
    """
    )

# 10. Accessibility - Iris (Goddess of the Rainbow and Divine Messenger)
iris = AssistantAgent(
    "Iris",
    model_client=model_client,
    system_message="""You are Iris, Goddess of the Rainbow and Messenger between Realms, who serves as the Accessibility reviewer.

    Your divine attributes:
    - Creator of bridges between different worlds
    - Bringer of color and light that all can perceive in their own way
    - Swift messenger ensuring communication reaches everyone

    As Iris, you speak with bright inclusivity and rainbow perspectives. You are compassionate and considerate of all readers' needs. You occasionally reference rainbows, bridges, or connecting realms when discussing accessibility.

    Your sacred duty is to ensure technical documentation is accessible to all by:
    - Checking that images have descriptive alt text for screen readers
    - Flagging instances of sensory language that assumes certain abilities
    - Evaluating color contrast if styling is used
    - Ensuring content is structured for navigability with assistive technologies

    When you find accessibility issues, clearly identify each problem, explain why it creates barriers for certain users, and provide accessible alternatives that serve all readers equally.

    End your reviews with a rainbow-inspired observation, such as "This document creates bridges to many readers, though several passages need wider spans to ensure all can cross regardless of their means of perception."
    
    Finally, at the bottom of your review, score the code quality on a scale of 0-100, where 100 is perfect accessibility.
    Assume high standards for production code. Output the score in the following format: "SCORE: [0-100]".
    """
    )

# 11. Visual Aid Suggestion - Dionysus (God of Wine, Festivities, and Theater)
dionysus = AssistantAgent(
    "Dionysus",
    model_client=model_client,
    system_message="""You are Dionysus, God of Wine, Ecstasy, and Theatre, who serves as the Visual Aid Suggestion reviewer.

    Your divine attributes:
    - Master of sensory experiences beyond mere words
    - Creator of visual spectacles and theatrical displays
    - Transformer who reveals new perspectives through altered perception

    As Dionysus, you speak with vibrant enthusiasm and creative inspiration. You are passionate about enhancing experiences through visual elements. You occasionally reference theater, celebrations, or transformation when discussing visual aids.

    Your sacred duty is to enhance documentation with appropriate visual elements by:
    - Identifying text-heavy sections that would benefit from diagrams, tables, or images
    - Suggesting specific types of visuals that would clarify complex concepts
    - Recommending placement of visual aids for maximum impact
    - Proposing visual hierarchies that guide the reader's attention

    When you identify opportunities for visual enhancement, specify the section, explain what type of visual would be beneficial, and describe what the visual should contain or demonstrate.

    End your reviews with a theatrical observation, such as "This textual performance could be elevated with several well-placed visual scenes to transform the audience's understanding, particularly at these dramatic moments."
    
    Finally, at the bottom of your review, score the code quality on a scale of 0-100, where 100 is perfect visual aid suggestion.
    Assume high standards for production code. Output the score in the following format: "SCORE: [0-100]".
    """
    )

######################################
# Meta & Experience Gods and Goddesses
######################################

# 12. Knowledge Decay - Chronos (Personification of Time and Aging)
chronos = AssistantAgent(
    "Chronos",
    model_client=model_client,
    system_message="""You are Chronos, Personification of Time and Inevitability, who serves as the Knowledge Decay reviewer.

    Your divine attributes:
    - Keeper of the passage of time and its effects on all things
    - Revealer of what has grown outdated or obsolete
    - Ancient observer who remembers the past while seeing into the future

    As Chronos, you speak with aged wisdom and temporal awareness. You are contemplative and mindful of change and evolution. You occasionally reference time, aging, or epochs when discussing information freshness.

    Your sacred duty is to identify outdated information in documentation by:
    - Comparing document timestamps against code/feature change logs
    - Flagging references to deprecated features, old versions, or outdated practices
    - Identifying terminology that has evolved or changed meaning over time
    - Noting areas where industry standards or best practices have moved forward

    When you find potentially outdated information, specify the content, explain why you believe it may be outdated, and suggest what aspects should be reviewed for possible updates.

    End your reviews with a time-oriented observation, such as "The sands of time have worn away the accuracy of several sections, particularly where the document speaks of methods that have since evolved into new forms."
    
    Finally, at the bottom of your review, score the code quality on a scale of 0-100, where 100 is perfect knowledge decay awareness.
    Assume high standards for production code. Output the score in the following format: "SCORE: [0-100]".
    """
    )

######################################
# Summarization & Organization Goddess
######################################

# 13. Summarization - Harmonia (Goddess of Harmony, Balance, and Concord)
harmonia = AssistantAgent(
    "Harmonia",
    model_client=model_client,
    system_message="""You are Harmonia, Goddess of Harmony and Concord, who serves as the Summary Report Generator.
    
    Your divine attributes:
    - Bringer of unity from diversity
    - Weaver of disparate threads into a cohesive tapestry
    - Mediator who finds balance among competing perspectives

    Your sacred duty is to create comprehensive summary reports of the Pantheon's feedback by:
    - Collecting and organizing all feedback from the divine reviewers to update the GitHub Actions step summary (GITHUB_STEP_SUMMARY)
    - Identifying areas of consensus and divergence among the reviewers
    - Distilling feedback into clear, actionable comments for GitHub PR review
    - Ensuring all feedback is properly attributed to the deity who provided it
    - Ensure the summary report contains the respective information from all 12 divine reviewers

    Your summary report should be formatted as:
    /* 
    * [DEITY: Deity name (Domain)]
    * [SCORE: 0-100] 
    * 
    * Feedback details...
    */

    End your summary with a statement about the harmony (or lack thereof) among the divine perspectives, 
    such as "The divine chorus offers a balanced harmony of perspectives, though several competing melodies 
    require resolution before perfection can be achieved."

    Once the summary is complete, please conclude with 'DOCUMENTATION REVIEW COMPLETE'.
    """
)


##########################
# Custom class definitions
##########################

# The new classes from Claude - v2    
class PRContentFetcher:
    """Class for fetching PR content and processing the diff."""
    
    def __init__(self, token: str, repo_name: str, pr_number: int):
        """
        Initialize the PR content fetcher.
        
        Args:
            token: GitHub personal access token
            repo_name: Repository name in format "username/repo"
            pr_number: PR number to fetch content from
        """
        self.g = Github(token)
        self.repo = self.g.get_repo(repo_name)
        self.pr = self.repo.get_pull(pr_number)
        
    def fetch_pr_diff(self) -> str:
        """
        Fetch the raw diff of the PR.
        
        Returns:
            Raw diff content as a string
        """
        return self.pr.get_diff().decoded_content.decode('utf-8')
    
    def fetch_pr_files(self) -> Dict[str, Dict]:
        """
        Fetch all files changed in the PR with their content.
        
        Returns:
            Dictionary mapping file paths to dictionaries containing file content and patch
        """
        files_dict = {}
        files = self.pr.get_files()
        
        for file in files:
            # Get the file content from the PR head (latest version)
            try:
                content = self.repo.get_contents(file.filename, ref=self.pr.head.ref).decoded_content.decode('utf-8')
            except Exception:
                content = "File content could not be retrieved"
            
            files_dict[file.filename] = {
                "content": content,
                "patch": file.patch,
                "status": file.status,  # 'added', 'removed', 'modified', etc.
                "changes": file.changes,
                "additions": file.additions,
                "deletions": file.deletions
            }
        
        return files_dict
    
    def process_pr_content(self) -> Tuple[str, Dict[str, Dict]]:
        """
        Process PR content for review by the divine team.
        
        Returns:
            Tuple containing:
            - Formatted PR content as a string
            - Dictionary of file contents for reference
        """
        files_dict = self.fetch_pr_files()
        pr_description = self.pr.body or "No description provided"
        
        # Format PR content for review
        formatted_content = f"# PR #{self.pr.number}: {self.pr.title}\n\n"
        formatted_content += f"## Description\n{pr_description}\n\n"
        formatted_content += f"## Changes\n\n"
        
        for filename, file_info in files_dict.items():
            formatted_content += f"### File: {filename}\n"
            formatted_content += f"Status: {file_info['status']}, " 
            formatted_content += f"Changes: +{file_info['additions']}, -{file_info['deletions']}\n\n"
            
            if file_info['patch']:
                formatted_content += "```diff\n"
                formatted_content += file_info['patch']
                formatted_content += "\n```\n\n"
            else:
                formatted_content += "No diff available for this file.\n\n"
        
        return formatted_content, files_dict

class DiffParser:
    """Class for parsing git diffs and mapping line numbers."""
    
    @staticmethod
    def parse_patch(patch: str) -> Dict[int, int]:
        """
        Parse a git patch to map original file line numbers to PR line numbers.
        
        Args:
            patch: The git patch string
        
        Returns:
            Dictionary mapping original line numbers to PR position numbers
        """
        line_map = {}
        file_line = 0
        position = 0
        
        lines = patch.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('@@'):
                # Parse the @@ -a,b +c,d @@ line to get starting line numbers
                match = re.match(r'^@@ -\d+,\d+ \+(\d+),\d+ @@', line)
                if match:
                    file_line = int(match.group(1)) - 1
                position = i
            elif not line.startswith('-'):
                # This is a line that appears in the new file
                file_line += 1
                position += 1
                if not line.startswith('+'):
                    # This line exists in both old and new file
                    line_map[file_line] = position
                else:
                    # This is a new line in the PR
                    line_map[file_line] = position
        
        return line_map
    
    @staticmethod
    def extract_sections_from_diff(patch: str) -> List[Dict]:
        """
        Extract meaningful sections from a git diff.
        
        Args:
            patch: The git patch string
        
        Returns:
            List of dictionaries containing section information
        """
        sections = []
        current_section = None
        current_lines = []
        line_number = 0
        
        lines = patch.split('\n')
        for line in lines:
            if line.startswith('@@'):
                # Start a new section
                if current_section:
                    current_section['lines'] = current_lines
                    sections.append(current_section)
                
                match = re.match(r'^@@ -\d+,\d+ \+(\d+),\d+ @@\s*(.*)', line)
                if match:
                    line_number = int(match.group(1)) - 1
                    section_name = match.group(2).strip() if match.group(2) else "Unnamed section"
                    current_section = {
                        'name': section_name,
                        'start_line': line_number,
                        'lines': []
                    }
                    current_lines = []
            elif current_section is not None:
                if not line.startswith('-'):
                    line_number += 1
                    if line.startswith('+'):
                        # Added line
                        current_lines.append({
                            'content': line[1:],
                            'line_number': line_number,
                            'type': 'added'
                        })
                    else:
                        # Context line
                        current_lines.append({
                            'content': line,
                            'line_number': line_number,
                            'type': 'context'
                        })
        
        # Add the last section
        if current_section:
            current_section['lines'] = current_lines
            sections.append(current_section)
        
        return sections

class DeityReviewParser:
    """Class for parsing and organizing deity feedback."""
    
    def __init__(self, messages, files_dict=None):
        """
        Initialize the parser with the chat messages.
        
        Args:
            messages: List of message dictionaries from the group chat
            files_dict: Dictionary of file contents for reference
        """
        self.messages = messages
        self.files_dict = files_dict or {}
        self.deity_reviews = {}
        self.section_reviews = {}
        self.file_line_reviews = {}
        self.combined_scores = {}
        
    def parse_reviews(self) -> Dict:
        """
        Parse the reviews from the chat messages.
        
        Returns:
            Dictionary of parsed reviews by deity
        """
        for message in self.messages:
            if message.source != "user" and message.source != "Harmonia":
                deity_name = message.source
                content = message.content
                
                # Extract score if present
                score_match = re.search(r'\*\*SCORE:\s*(\d+|N/A)\*\*', content)
                score = score_match.group(1) if score_match else "N/A"
                
                # Store the review content and score
                self.deity_reviews[deity_name] = {
                    "content": content,
                    "score": score
                }
                
                # Extract file-specific reviews
                self._extract_file_specific_reviews(deity_name, content, score)
                
        # Calculate average scores by deity
        for deity, review in self.deity_reviews.items():
            if review["score"] != "N/A":
                try:
                    self.combined_scores[deity] = int(review["score"])
                except ValueError:
                    pass
        
        return self.deity_reviews
    
    def _extract_file_specific_reviews(self, deity_name: str, content: str, score: str):
        """
        Extract file and line specific reviews from the content.
        
        Args:
            deity_name: Name of the deity providing the review
            content: Review content
            score: Review score
        """
        # Look for file references
        file_patterns = [
            r'File:\s*([^\n,]+)',
            r'file\s+([^\n,]+)',
            r'in\s+([^\s]+\.(py|js|ts|css|html|md|txt|json))',
        ]
        
        for pattern in file_patterns:
            file_matches = re.finditer(pattern, content, re.IGNORECASE)
            for file_match in file_matches:
                filename = file_match.group(1).strip()
                
                # Look for line number references near this file mention
                line_context = content[file_match.start():file_match.start() + 300]
                line_matches = re.finditer(r'[Ll]ine\s+(\d+)', line_context)
                
                for line_match in line_matches:
                    line_num = int(line_match.group(1))
                    
                    # Find the issue and recommendation in this vicinity
                    issue_context = line_context[line_match.start():line_match.start() + 300]
                    comment = self._extract_comment_from_context(issue_context)
                    
                    file_line_key = f"{filename}:{line_num}"
                    if file_line_key not in self.file_line_reviews:
                        self.file_line_reviews[file_line_key] = []
                    
                    self.file_line_reviews[file_line_key].append({
                        "deity": deity_name,
                        "comment": comment,
                        "score": score
                    })
        
        # Also check for line-only references (when file is implied)
        line_matches = re.finditer(r'[Ll]ine\s+(\d+)', content)
        for line_match in line_matches:
            line_num = int(line_match.group(1))
            
            # Look for quoted content after this line reference
            quoted_content = self._find_quoted_content_after_match(content, line_match)
            if quoted_content:
                comment = self._extract_comment_for_quote(content, quoted_content, line_match.end())
                
                # Since we don't know the file, use a generic key
                key = f"line:{line_num}"
                if key not in self.section_reviews:
                    self.section_reviews[key] = []
                
                self.section_reviews[key].append({
                    "deity": deity_name,
                    "comment": comment,
                    "score": score
                })
    
    def _find_quoted_content_after_match(self, content: str, match) -> Optional[str]:
        """Find quoted content after a regex match."""
        start_idx = match.end()
        remaining = content[start_idx:start_idx + 300]  # Look at the next 300 chars
        
        # Try quoted content patterns
        patterns = [
            r'"([^"]+)"',          # Double quotes
            r'\'([^\']+)\'',       # Single quotes
            r'`([^`]+)`',          # Backticks
            r'Content:\s*"?([^"\n]+)"?',  # Content: label
            r'Text:\s*"?([^"\n]+)"?',     # Text: label
            r'Quoted Content:\s*"?([^"\n]+)"?',  # Quoted Content: label
            r'Current:\s*"?([^"\n]+)"?',  # Current: label
        ]
        
        for pattern in patterns:
            quote_match = re.search(pattern, remaining)
            if quote_match:
                for group in quote_match.groups():
                    if group:
                        return group.strip()
        
        return None
    
    def _extract_comment_from_context(self, context: str) -> str:
        """Extract review comment from a context string."""
        # Look for issue/concern patterns
        issue_patterns = [
            r'(?:Issue|Concern|Challenge|Opportunity):\s*([^\n]+)',
            r'(?:Why it challenges readers):\s*([^\n]+)',
            r'(?:Cognitive Overload Concern):\s*([^\n]+)',
        ]
        
        # Look for recommendation patterns
        rec_patterns = [
            r'(?:Recommendation|Suggestion|Corrected Alternative|Simplified Version):\s*([^\n]+)',
            r'(?:Guideline):\s*([^\n]+)',
        ]
        
        comment = ""
        
        # Extract issue
        for pattern in issue_patterns:
            issue_match = re.search(pattern, context)
            if issue_match:
                comment += f"Issue: {issue_match.group(1).strip()}\n"
                break
        
        # Extract recommendation
        for pattern in rec_patterns:
            rec_match = re.search(pattern, context)
            if rec_match:
                comment += f"Suggestion: {rec_match.group(1).strip()}"
                break
        
        # If still no comment, extract a general chunk of text
        if not comment:
            # Find paragraphs after potential issue indicators
            indicators = ["Issue", "Problem", "Error", "Concern", "Challenge"]
            for indicator in indicators:
                indicator_match = re.search(f'{indicator}[s]?[:\.\s]', context, re.IGNORECASE)
                if indicator_match:
                    start_idx = indicator_match.end()
                    end_idx = context.find("\n\n", start_idx)
                    if end_idx == -1:
                        end_idx = len(context)
                    comment = context[start_idx:end_idx].strip()
                    break
        
        # If still no comment, take the first substantial paragraph
        if not comment:
            paragraphs = re.split(r'\n\s*\n', context)
            for para in paragraphs:
                cleaned = para.strip()
                if len(cleaned) > 30 and not cleaned.startswith('#') and not cleaned.startswith('-'):
                    comment = cleaned
                    break
        
        # If still nothing, use a generic message
        if not comment:
            comment = "See general feedback for details"
            
        return comment
    
    def _extract_comment_for_quote(self, content: str, quoted_text: str, start_offset: int = 0) -> str:
        """Extract the comment related to a quoted piece of text."""
        start_idx = content.find(quoted_text, start_offset)
        if start_idx == -1:
            return "See general feedback"
        
        # Look for the next section in the review (within 500 chars after the quote)
        remaining = content[start_idx + len(quoted_text):start_idx + len(quoted_text) + 500]
        
        return self._extract_comment_from_context(remaining)

class GitHubPRReviewer:
    """Class for posting review comments to GitHub PR."""
    
    def __init__(self, token: str, repo_name: str, pr_number: int):
        """
        Initialize the GitHub PR reviewer.
        
        Args:
            token: GitHub personal access token
            repo_name: Repository name in format "username/repo"
            pr_number: PR number to comment on
        """
        self.g = Github(token)
        self.repo = self.g.get_repo(repo_name)
        self.pr = self.repo.get_pull(pr_number)
        
    def add_file_line_comments(self, file_line_reviews: Dict[str, List[Dict]], files_dict: Dict[str, Dict]):
        """
        Add comments to specific file lines in the PR.
        
        Args:
            file_line_reviews: Dictionary mapping "file:line" to lists of review comments
            files_dict: Dictionary of file contents and patches
        """
        # Create a map of filename to DiffParser results
        file_maps = {}
        for filename, file_info in files_dict.items():
            if file_info.get('patch'):
                file_maps[filename] = DiffParser.parse_patch(file_info['patch'])
        
        # Process each file:line comment
        for file_line_key, reviews in file_line_reviews.items():
            if ':' not in file_line_key:
                continue
                
            filename, line_str = file_line_key.split(':', 1)
            try:
                line_num = int(line_str)
            except ValueError:
                continue
            
            # Check if we can map this file/line to a position in the PR
            if filename in file_maps and line_num in file_maps[filename]:
                position = file_maps[filename][line_num]
                
                # Combine the deity comments for this line
                comment_body = f"## Divine Review Panel Feedback for Line {line_num}\n\n"
                
                for review in reviews:
                    comment_body += f"### {review['deity']} (Score: {review['score']})\n"
                    comment_body += f"{review['comment']}\n\n"
                
                # Add the comment to the PR
                try:
                    self.pr.create_review_comment(
                        body=comment_body,
                        commit_id=self.pr.get_commits().get_page(0)[-1].sha,
                        path=filename,
                        position=position
                    )
                except Exception as e:
                    print(f"Error creating review comment for {file_line_key}: {e}")
    
    def add_section_comments(self, section_reviews: Dict, files_dict: Dict[str, Dict]):
        """
        Add comments to sections where file is unknown but line is known.
        
        Args:
            section_reviews: Dictionary mapping section keys to lists of review comments
            files_dict: Dictionary of file contents and patches
        """
        # For lines without explicit file references, try to map to all changed files
        for key, reviews in section_reviews.items():
            if key.startswith("line:"):
                line_num = int(key.split(":", 1)[1])
                
                # Try to find this line in each file
                for filename, file_info in files_dict.items():
                    if file_info.get('patch'):
                        line_map = DiffParser.parse_patch(file_info['patch'])
                        if line_num in line_map:
                            # Found a matching line, add the comment
                            position = line_map[line_num]
                            
                            comment_body = f"## Divine Review Panel Feedback for Line {line_num}\n\n"
                            
                            for review in reviews:
                                comment_body += f"### {review['deity']} (Score: {review['score']})\n"
                                comment_body += f"{review['comment']}\n\n"
                            
                            try:
                                self.pr.create_review_comment(
                                    body=comment_body,
                                    commit_id=self.pr.get_commits().get_page(0)[-1].sha,
                                    path=filename,
                                    position=position
                                )
                            except Exception as e:
                                print(f"Error creating review comment for {key} in {filename}: {e}")
    
    def add_summary_comment(self, deity_reviews: Dict, combined_scores: Dict):
        """
        Add a summary comment to the PR with overall feedback.
        
        Args:
            deity_reviews: Dictionary of deity reviews
            combined_scores: Dictionary of deity scores
        """
        # Calculate average score
        if combined_scores:
            avg_score = sum(combined_scores.values()) / len(combined_scores)
        else:
            avg_score = "N/A"
        
        # Create summary comment
        comment = f"# Divine Review Panel: Summary Report\n\n"
        comment += f"## Overall Assessment\n"
        comment += f"Average Score: {avg_score if avg_score != 'N/A' else 'N/A'}/100\n\n"
        
        comment += "## Individual Deity Assessments\n\n"
        for deity, score in combined_scores.items():
            comment += f"- **{deity}**: {score}/100\n"
        
        comment += "\n## Key Observations\n\n"
        
        # Extract key takeaways from each deity
        for deity, review in deity_reviews.items():
            content = review["content"]
            
            # Try to find the conclusion paragraph
            conclusion = None
            if "\"" in content:
                quote_matches = list(re.finditer(r'"([^"]+)"', content))
                if quote_matches:
                    # Get the last quote which is often the conclusion
                    conclusion = quote_matches[-1].group(1)
            
            if not conclusion:
                paragraphs = content.split("\n\n")
                for para in reversed(paragraphs):
                    if para and "SCORE" not in para and len(para) > 30:
                        conclusion = para
                        break
            
            if conclusion:
                comment += f"### {deity}\n"
                comment += f"{conclusion}\n\n"
        
        # Add the summary comment to the PR
        self.pr.create_issue_comment(comment)

####################
# PyGithub functions
####################

async def run_review_and_comment(token: str, repo_name: str, pr_number: int):
    """
    Run the divine review panel and post comments to GitHub PR.
    
    Args:
        token: GitHub personal access token
        repo_name: Repository name in format "username/repo"
        pr_number: PR number to comment on
    """
    
    # Fetch PR content
    pr_fetcher = PRContentFetcher(token, repo_name, pr_number)
    formatted_content, files_dict = pr_fetcher.process_pr_content()

    #######################################
    # AutoGen team and behavior definitions
    #######################################

    # Define a termination condition that stops the task if a special phrase is mentioned
    text_termination = TextMentionTermination("DOCUMENTATION REVIEW COMPLETE")

    # Create a team with all the Greek gods and goddesses
    greek_pantheon_team = RoundRobinGroupChat(
        [apollo, hermes, athena, hestia, mnemosyne, hephaestus, heracles, demeter, aphrodite, iris, dionysus, chronos, harmonia], 
        termination_condition=text_termination
    )

# Create the task description with the PR content
    task = f"""Your task is to review the following changes from pull requests according to your divine domain of expertise. Instructions:
- Provide the response in following JSON format:  {{\"reviews\": [{{\"lineNumber\":  <line_number>, \"reviewComment\": \"<review comment>\"}}]}}
- Do not give positive comments or compliments.
- Write the comment in GitHub Markdown format.
- IMPORTANT: NEVER suggest adding comments to the code.
- IMPORTANT: When referring to specific code, please include the filename and line number in this format: [SECTION: filename:line_number]

Review the following code diff:
{formatted_content}

Your feedback should be specific, constructive, and actionable.
"""
       
    # Run the review
    divine_responses = await greek_pantheon_team.run(task=task)
    
    # Parse the reviews
    parser = DeityReviewParser(divine_responses.messages, files_dict)
    deity_reviews = parser.parse_reviews()
    
    # Post comments to GitHub PR
    reviewer = GitHubPRReviewer(token, repo_name, pr_number)
    reviewer.add_file_line_comments(parser.file_line_reviews, files_dict)
    reviewer.add_section_comments(parser.section_reviews, files_dict)
    reviewer.add_summary_comment(deity_reviews, parser.combined_scores)
    
    # Close the connection to the model client
    await model_client.close()
    
    return divine_responses


# Entry point for the GitHub Action - v2
if __name__ == "__main__":

    # Run the review and comment process
    asyncio.run(run_review_and_comment(
        token=github_token,
        repo_name=repository,
        pr_number=pr_number
    ))