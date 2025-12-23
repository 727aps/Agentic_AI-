# Real Estate Agent

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)

## Overview

An AI-powered real estate agent that leverages Google's ADK (Agent Development Kit) and multiple AI services to provide comprehensive real estate analysis, market insights, and property recommendations. The system combines various data sources and AI models to assist with real estate decision-making.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables for API access:
```bash
export GROQ_API_KEY=your_groq_api_key
```

3. Run the notebook:
```bash
cd notebooks
jupyter notebook "Real Estate Agent.ipynb"
```

## Architecture

- **Google ADK Framework**: Core agent development platform
- **LiteLLM Integration**: Unified interface for multiple LLM providers
- **Gradio Interface**: Web-based UI for user interaction
- **Multi-modal Analysis**: Combines text, data, and potentially visual analysis

## Key Dependencies

- google-adk: Google's Agent Development Kit
- google-generativeai: Google's Generative AI services
- litellm: Unified LLM API interface
- gradio: Web UI framework
- httpx: HTTP client library

## Features

- Real estate market analysis
- Property recommendations
- Interactive web interface
- Integration with multiple AI services

## License

This project is part of the Agentic AI Projects repository. See main repository for license information.

## Contributing

Follow the main repository's contributing guidelines. Ensure all API keys are properly secured using environment variables.
