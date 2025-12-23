# Code Reviews with PR Agent

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)

## Overview

An AI-powered code review system that automates the analysis of GitHub pull requests using LangGraph for workflow orchestration and local Ollama models for intelligent code analysis. The system fetches PR diffs from GitHub and provides comprehensive code review suggestions through a structured agent-based workflow.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export GITHUB_TOKEN=your_github_personal_access_token
```

3. Ensure Ollama is running locally:
```bash
# Install and run Ollama
ollama serve
ollama pull tinyllama  # or your preferred model
```

4. Update repository configuration in `review.py`:
```python
REPO = "your-username/your-repo"
PR_NUMBER = your_pr_number
```

5. Run the code review:
```bash
python review.py
```

## Architecture

The system uses LangGraph for orchestrating the code review workflow:

- **Load Diff Node**: Fetches and loads PR diff from GitHub API
- **Review Node**: Analyzes code changes using local Ollama model
- **Display Node**: Presents formatted review results

## Key Dependencies

- langgraph: Workflow orchestration framework
- langchain: LLM integration utilities
- requests: HTTP client for GitHub API
- ollama: Local LLM inference (external dependency)

## Features

- Automated GitHub PR diff fetching
- AI-powered code review generation
- Local model inference (no external API costs)
- Structured review workflow with LangGraph
- Comprehensive code analysis suggestions
- Support for multiple programming languages

## Workflow

1. **PR Diff Retrieval**: Fetches diff from GitHub API using personal access token
2. **Code Analysis**: Local Ollama model analyzes changes for:
   - Code quality issues
   - Potential bugs
   - Best practices violations
   - Security concerns
   - Performance optimizations
3. **Review Generation**: Structured feedback with actionable suggestions

## Configuration

- Update `REPO` and `PR_NUMBER` in `review.py` for your target PR
- Modify the Ollama model in the payload (currently uses "tinyllama")
- Adjust analysis prompts for specific coding standards

## Additional Scripts

- `calculator.py`: Utility functions
- `fetch_diff-ui.py`: Alternative UI for diff fetching
- `diff.patch`: Sample/generated patch file

## License

This project is part of the Agentic AI Projects repository. See main repository for license information.

## Contributing

Follow the main repository's contributing guidelines. Ensure all API keys are properly secured using environment variables.
