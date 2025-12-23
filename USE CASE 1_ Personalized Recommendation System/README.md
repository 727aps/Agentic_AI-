# Personalized Recommendation System

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)

## Overview

An AI-powered personalized recommendation system that leverages multiple data sources and machine learning techniques to provide tailored recommendations. The system uses CrewAI framework with specialized agents for content analysis, user preference modeling, and recommendation generation.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables for API access:
```bash
export GROQ_API_KEY=your_groq_api_key
export HF_TOKEN=your_huggingface_token
export FIRECRAWL_API_KEY=your_firecrawl_api_key
```

3. Run the notebook:
```bash
cd notebooks
jupyter notebook "Final Personalized Recommendation system AI .ipynb"
```

## Architecture

- **Content Analysis Agent**: Processes and analyzes various content sources
- **User Preference Agent**: Models user preferences and behavior patterns
- **Recommendation Engine**: Combines multiple signals to generate personalized recommendations
- **CrewAI Framework**: Orchestrates agent interactions and workflows

## Key Dependencies

- crewai: Multi-agent framework
- crewai_tools: Agent tools and utilities
- langchain-huggingface: Hugging Face integrations
- groq: Fast inference API
- faiss-cpu: Vector similarity search
- firecrawl-py: Web scraping and content extraction

## License

This project is part of the Agentic AI Projects repository. See main repository for license information.

## Contributing

Follow the main repository's contributing guidelines. Ensure all API keys are properly secured using environment variables.
