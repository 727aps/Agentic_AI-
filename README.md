# Agentic AI Projects

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

This repository contains 6 different Agentic AI use cases implemented with various AI frameworks and APIs. Each project follows best practices with organized structure, comprehensive documentation, and secure API key management.

## Project Structure

### 📊 USE CASE 1: Personalized Recommendation System
- **Location**: `USE CASE 1_ Personalized Recommendation System/`
- **Technology**: CrewAI, LangChain, Groq API
- **Features**: Multi-source content analysis, personalized recommendations
- **Files**: `notebooks/`, `requirements.txt`, `README.md`

### 📄 USE CASE 2: Document Analysis Agent
- **Location**: `USE CASE 2_ Document Analysis Agent/`
- **Technology**: Multi-agent Python application
- **Features**: Document extraction, structuring, finance analysis, RAG
- **Files**: `agents/`, `main.py`, `storage/`

### ✈️ USE CASE 3: Travel Planner
- **Location**: `USE CASE 3 _ Travel Planner/`
- **Technology**: Streamlit, Phi framework, Groq API
- **Features**: AI-powered travel planning and recommendations
- **Files**: `main.py`, `requirements.txt`, `Output/`

### 🏠 USE CASE 4: Real Estate Agent
- **Location**: `USE CASE 4_ Real Estate Agent/`
- **Technology**: Google ADK, LiteLLM, Gradio
- **Features**: Real estate analysis and market insights
- **Files**: `notebooks/`, `requirements.txt`, `README.md`

### 🏥 USE CASE 5: Health Care Agent
- **Location**: `USE CASE 5_ Health Care Agent/`
- **Technology**: CrewAI, LangChain, PyMuPDF
- **Features**: Medical document analysis, healthcare recommendations
- **Files**: `notebooks/`, `requirements.txt`, `README.md`

### 🔍 USE CASE 6: Code Reviews with PR Agent
- **Location**: `USE CASE 6 _ CODE REVIEWS WITH PR AGENT/`
- **Technology**: LangGraph, Ollama, GitHub API
- **Features**: AI-powered code review and PR analysis
- **Files**: `review.py`, `requirements.txt`, supporting scripts

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
