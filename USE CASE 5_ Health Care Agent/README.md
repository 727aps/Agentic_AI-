# Health Care Agent

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)

## Overview

An AI-powered healthcare assistant that combines CrewAI framework with document processing capabilities to provide intelligent healthcare analysis, medical document interpretation, and health-related recommendations. The system can process medical documents, analyze health data, and provide insights for healthcare decision-making.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables for API access:
```bash
export GROQ_API_KEY=your_groq_api_key
export HF_TOKEN=your_huggingface_token
```

3. Run the notebook:
```bash
cd notebooks
jupyter notebook "AI in health care .ipynb"
```

## Architecture

- **CrewAI Framework**: Multi-agent orchestration for healthcare tasks
- **Document Processing**: PyMuPDF integration for medical document analysis
- **LangChain Integration**: Advanced language model chaining and processing
- **Gradio Interface**: User-friendly web interface for healthcare interactions

## Key Dependencies

- crewai: Multi-agent framework
- langchain: LLM application framework
- langchain-community: Community integrations
- pymupdf: PDF processing library
- gradio: Web UI framework
- openai: OpenAI API integration

## Features

- Medical document analysis
- Health data interpretation
- AI-powered healthcare recommendations
- Interactive web interface
- Multi-agent healthcare workflows

## License

This project is part of the Agentic AI Projects repository. See main repository for license information.

## Contributing

Follow the main repository's contributing guidelines. Ensure all API keys are properly secured using environment variables.
