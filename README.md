# Agentic AI Projects

This repository contains 6 different Agentic AI use cases implemented with various AI frameworks and APIs.

## Project Structure

- **USE CASE 1**: Personalized Recommendation System - AI-powered recommendation engine
- **USE CASE 2**: Document Analysis Agent - Multi-agent system for document processing and analysis
- **USE CASE 3**: Travel Planner - AI travel planning assistant
- **USE CASE 4**: Real Estate Agent - Real estate analysis and recommendations
- **USE CASE 5**: Health Care Agent - AI healthcare assistant
- **USE CASE 6**: Code Reviews with PR Agent - AI-powered code review system

## Setup Instructions

### Environment Variables

Before running any of the notebooks or scripts, set up the following environment variables with your own API keys:

```bash
# Groq API Key (used in multiple use cases)
export GROQ_API_KEY=your_groq_api_key_here

# Hugging Face Token (used in recommendation and healthcare agents)
export HF_TOKEN=your_huggingface_token_here

# GitHub Personal Access Token (used in code review agent)
export GITHUB_TOKEN=your_github_token_here

# Firecrawl API Key (used in document analysis)
export FIRECRAWL_API_KEY=your_firecrawl_key_here
```

### Installation

Each use case may have specific requirements. Check the `requirements.txt` files in individual project folders for dependencies.

## Security Note

All API keys and tokens have been replaced with placeholders (`"add_your_api_key"`) in the code. Never commit actual API keys to version control.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure no secrets are committed
5. Submit a pull request
