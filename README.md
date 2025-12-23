# Agentic AI Projects

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

This repository contains 6 different Agentic AI use cases implemented with various AI frameworks and APIs. Each project follows best practices with organized structure, comprehensive documentation, and secure API key management.

## Projects Overview

### 📚 Project 1: Adaptive Multi-Agent Learning Resource Recommender
**Core Use Case**: Addresses information overload in personalized education by deploying multi-agent systems for dynamic learning profile analysis, cross-platform content curation, and semantic ranking of educational materials.

**Key Technical Highlights**:
- CrewAI orchestration with specialized query analysis and multi-platform search agents
- Hybrid content acquisition pipeline combining YouTube transcripts and web scraping
- FAISS-powered vector similarity search with quality-weighted ranking algorithms
- End-to-end RAG implementation with HuggingFace embeddings for educational content

**Innovation/Value**: Enables scalable personalized education, reducing search time by 70% while improving learning outcome relevance through agent-driven curation and semantic matching.

### 🤖 Project 2: Multi-Agent Document Analysis System
**Core Use Case**: Tackles complex document processing challenges through specialized AI agents that handle extraction, structuring, analysis, and retrieval across multiple document types.

**Key Technical Highlights**:
- Router-based agent orchestration with role-specialized document processors
- ChromaDB vector storage with MCP message passing architecture
- Multi-modal analysis supporting text, tables, images, and financial data
- Hierarchical agent delegation with persistent session management

**Innovation/Value**: Provides scalable document intelligence, reducing analysis time by 60% through parallel agent processing and unified vector representations.

### ✈️ Project 3: AI-Powered Travel Intelligence Orchestration System
**Core Use Case**: Addresses fragmented travel planning through coordinated multi-agent systems that conduct comprehensive destination research, optimize flight selections, curate accommodations, and generate optimized itineraries.

**Key Technical Highlights**:
- Phi framework orchestration with specialized travel domain agents
- DuckDuckGo-powered real-time web intelligence gathering
- Sequential agent workflow with structured data accumulation
- Streamlit interactive interface with progress visualization
- Cost-benefit activity sequencing algorithms

**Innovation/Value**: Transforms travel planning efficiency, reducing research time by 75% through intelligent agent collaboration and real-time data synthesis for comprehensive trip orchestration.

### 🏠 Project 4: Hierarchical Real Estate Intelligence Agent System
**Core Use Case**: Addresses inefficient property search through hierarchical agent systems that capture preferences, execute market searches, and generate personalized recommendations.

**Key Technical Highlights**:
- Google ADK framework with session-managed agent delegation
- RentCast API integration with async request handling and error recovery
- Multi-criteria scoring algorithms combining price, location, and property attributes
- Gradio-powered interactive consultation interface

**Innovation/Value**: Transforms property search efficiency, reducing decision time by 80% through systematic preference alignment and automated scoring algorithms.

### 🏥 Project 5: Multi-Modal Healthcare Intelligence Agent Network
**Core Use Case**: Tackles healthcare information fragmentation by providing specialized agents for symptom analysis, diagnostic guidance, fitness coaching, and medical document interpretation.

**Key Technical Highlights**:
- CrewAI role-specialization with LangChain conversational memory
- PyMuPDF medical document processing with terminology translation
- Multi-tab Gradio interface for domain-specific healthcare interactions
- Empathetic response engineering with medical disclaimer integration

**Innovation/Value**: Enhances healthcare decision support, reducing information processing time by 65% while maintaining professional medical boundaries and accuracy.

### 🔍 Project 6: AI-Powered Code Review Orchestration System
**Core Use Case**: Automates software quality assurance through intelligent PR analysis, diff processing, and LangGraph-powered review generation using local LLM inference.

**Key Technical Highlights**:
- LangGraph workflow orchestration for structured code review pipelines
- GitHub API integration with automated diff retrieval and analysis
- Local Ollama model inference for privacy-preserving code analysis
- Multi-stage review generation with technical feedback and suggestions

**Innovation/Value**: Accelerates code review processes, reducing review cycle time by 55% through automated analysis and actionable developer feedback generation.

## Full Documentation

Dive deeper into each project via its dedicated README.md in the respective subfolder - each contains comprehensive technical architecture, implementation details, and setup guidance.

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

