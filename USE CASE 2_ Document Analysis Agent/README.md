# Document Analysis Agent

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)

## Overview

A sophisticated multi-agent document analysis system that leverages specialized AI agents to process, analyze, and interpret various types of documents including text, tables, images, and financial data. The system uses a router-based architecture with ChromaDB for vector storage and Gradio for user interaction.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables for API access:
```bash
export GROQ_API_KEY=your_groq_api_key
export FIRECRAWL_API_KEY=your_firecrawl_api_key
export CHROMA_PERSIST_DIRECTORY=storage/chroma
```

3. Run the application:
```bash
python main.py
```

## Architecture

The system employs a modular multi-agent architecture:

- **RouterAgent**: Orchestrates requests and routes them to appropriate specialized agents
- **KnowledgeBaseAgent**: Manages document storage and retrieval in vector database
- **RAGBotAgent**: Provides retrieval-augmented generation for document queries
- **FinanceAgent**: Specializes in financial document analysis and insights
- **DocumentExtractionAgent**: Handles initial document parsing and extraction
- **DocumentStructuringAgent**: Organizes and structures extracted document content
- **TextInterpreterAgent**: Analyzes and interprets textual content
- **TableInterpreterAgent**: Processes and analyzes tabular data
- **ImageInterpreterAgent**: Handles image and visual content analysis

## Key Dependencies

- gradio: Web interface framework
- chromadb: Vector database for document embeddings
- python-dotenv: Environment variable management
- asyncio: Asynchronous programming support

## Features

- Multi-modal document processing (text, tables, images)
- Intelligent routing based on document type and query
- Vector-based document storage and retrieval
- Real-time analysis through web interface
- Specialized agents for different document types
- Persistent storage with ChromaDB

## Document Types Supported

- Text documents and articles
- Financial reports and statements
- Structured tabular data
- Images and visual content
- Mixed multi-modal documents

## License

This project is part of the Agentic AI Projects repository. See main repository for license information.

## Contributing

Follow the main repository's contributing guidelines. Ensure all API keys are properly secured using environment variables.
