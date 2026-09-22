# DataCortex

> AI-powered natural language interface for relational databases.

[![Tests](https://img.shields.io/badge/tests-141%20passed-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.14%2B-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141%2B-009688)]()
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000)]()
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

**DataCortex** lets users query relational databases using natural language instead of writing SQL manually.

For example:

> "Show me total sales"

DataCortex sends the request through an AI-assisted query pipeline that generates SQL, cleans and validates it, checks it against the discovered database schema, applies database security policies, executes it through a database abstraction layer, and turns the result into a natural-language answer.

The project is designed with **clean architecture principles and separation of concerns**, keeping API handling, AI services, SQL processing, database access, validation, and security independently testable.

---

## Why DataCortex?

A basic Text-to-SQL demo can stop after:

```text
Natural Language
       ↓
LLM
       ↓
SQL
       ↓
Database
```

DataCortex treats Text-to-SQL as a **backend engineering problem**, adding validation, schema awareness, database abstraction, security controls, retrieval, agents, and automated tests around the LLM.

```text
User Question
      │
      ▼
   FastAPI
      │
      ▼
 AI Query Service
      │
      ├── Text-to-SQL
      ├── RAG
      ├── Entity Resolution
      └── Agent / Tool Calling
      │
      ▼
 SQL Cleaning
      │
      ▼
 SQL Validation
      │
      ▼
 Schema Validation
      │
      ▼
 Security Policy
      │
      ▼
 Database Adapter
      │
      ▼
 Database Dialect
      │
      ▼
 SQL Execution
      │
      ▼
 Natural-Language Answer
```

---

## Key Features

- **Natural Language → SQL**
- **Schema-aware SQL generation**
- **SQL cleaning and validation**
- **SELECT-only query enforcement**
- **Multiple-statement protection**
- **Schema-aware validation**
- **Database query row limits**
- **Post-execution result-size validation**
- **PostgreSQL support**
- **MySQL and SQL Server dialect support**
- **Structured LLM output**
- **Function and tool calling**
- **AI agent workflow**
- **RAG-based knowledge retrieval**
- **Semantic search with embeddings**
- **Entity resolution**
- **Natural-language answer generation**
- **Automated test suite**
- **Ruff and pre-commit**
- **Docker / Docker Compose**
- **GitHub Actions CI**

---

# Architecture

DataCortex separates API, AI, SQL, database, and security responsibilities.

## Main Request Flow

```text
User
  │
  │ Natural Language Query
  ▼
FastAPI
  │
  ▼
AI Query Service
  │
  ├── LLM
  │    └── Text-to-SQL
  │
  ▼
SQL Cleaner
  │
  ▼
SQL Validator
  │
  ▼
Schema Validation
  │
  ▼
Database Security Policy
  │
  ▼
Database Adapter
  │
  ▼
Database Dialect
  │
  ├── PostgreSQL
  ├── MySQL
  └── SQL Server
  │
  ▼
SQL Execution
  │
  ▼
Query Result
  │
  ▼
Natural-Language Answer
```

## AI Components

```text
                    ┌─────────────────┐
                    │   User Query    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    AI Agent     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        Tool Calling        RAG        Entity Resolution
              │              │              │
              ▼              ▼              ▼
        Database Tools   Embeddings     Entity Matching
              │
              ▼
        SQL Execution
```

## Architectural Principles

- Separation of concerns
- Service-oriented business logic
- Database abstraction through adapters and dialects
- Database-specific behavior isolated behind abstractions
- Independent validation and security policies
- Schema-aware SQL processing
- Testable components
- Separation between API, AI, SQL, and database layers

---

# AI Pipeline

## Text-to-SQL

The Text-to-SQL pipeline uses the discovered database schema to provide context to the LLM before SQL generation.

```text
Natural Language
       │
       ▼
Schema Discovery
       │
       ▼
Schema-aware Prompt
       │
       ▼
LLM
       │
       ▼
Generated SQL
       │
       ▼
SQL Cleaner
       │
       ▼
SQL Validator
```

## Structured LLM Output

LLM responses can be represented using structured application schemas rather than relying only on free-form text.

This makes downstream processing more predictable and testable.

## AI Agent and Tool Calling

The project includes an agent workflow where the model can interact with application tools such as database-related operations.

```text
User
 │
 ▼
AI Agent
 │
 ├── Tool Selection
 │
 ├── Tool Execution
 │
 └── Final Response
```

## RAG and Semantic Search

```text
Knowledge
    │
    ▼
Embedding Model
    │
    ▼
Vector Representation
    │
    ▼
Semantic Search
    │
    ▼
Relevant Knowledge
    │
    ▼
LLM
```

The embedding pipeline uses `sentence-transformers` for semantic representations.

## Entity Resolution

```text
User Term
   │
   ▼
Embedding
   │
   ▼
Similarity Search
   │
   ▼
Candidate Entities
   │
   ▼
Resolved Entity
```

---

# Database Architecture

Database-specific behavior is isolated behind adapters and dialects.

```text
DatabaseAdapter
       │
       ▼
DatabaseDialect
       │
 ┌─────┼──────────┐
 ▼     ▼          ▼
PostgreSQL       MySQL       SQL Server
```

The abstraction isolates database-specific behavior such as:

- SQL placeholders
- Query-limit syntax
- Database selection
- Dialect-specific SQL behavior

Higher-level query execution code does not need to contain database-specific branching for these concerns.

### Current Database Support

| Database | Status |
|----------|--------|
| PostgreSQL | Supported |
| MySQL | Supported through dialect abstraction |
| SQL Server | Supported through dialect abstraction |

---

# Security

DataCortex does not treat LLM-generated SQL as trusted input.

```text
Generated SQL
     │
     ▼
1. SQL Validation
     │
     ▼
2. Schema Validation
     │
     ▼
3. Database Security Policy
     │
     ▼
4. Database-specific Row Limit
     │
     ▼
5. Post-execution Row-count Validation
     │
     ▼
SQL Execution
```

## Security Layers

| Layer | Purpose |
|------|---------|
| SQL Validation | Reject non-SELECT and unsafe SQL patterns |
| Multiple-statement protection | Prevent multiple SQL statements |
| Schema Validation | Ensure referenced tables and columns exist |
| Security Policy | Apply database-query security rules |
| Row Limit | Prevent unbounded result sets |
| Post-execution Check | Verify returned row count |

The default maximum result size is **1000 rows**.

> **LLM output is treated as untrusted input.**

---

# What Makes DataCortex Different?

| Area | Basic Text-to-SQL Demo | DataCortex |
|------|-------------------------|------------|
| SQL generation | LLM → SQL | Schema-aware generation |
| Validation | Often minimal | SQL + schema validation |
| Security | Basic filtering | Dedicated security policy + row limits |
| Database support | Usually one DB | Database abstraction + dialects |
| AI capabilities | Text-to-SQL | Text-to-SQL + RAG + Agent + Embeddings + Entity Resolution |
| Testing | Manual examples | Automated test suite |
| Infrastructure | Local process | Docker / Compose |
| Code quality | Ad hoc | Ruff + pre-commit + CI |
| Backend focus | Demo | Layered backend architecture |

---

# Challenges & Solutions

| Challenge | Approach |
|-----------|----------|
| LLM-generated SQL cannot be trusted | Validation and security layers before execution |
| LLM may reference invalid tables or columns | Schema discovery + schema-aware validation |
| Different databases use different SQL behavior | Adapter and dialect abstraction |
| Large result sets can be expensive | Database-specific row limits |
| LLM responses can be inconsistent | Structured application schemas |
| Natural-language terms may not match DB entities exactly | Entity-resolution layer |
| Relevant database knowledge may be large | Semantic retrieval / RAG |
| AI workflows may require multiple operations | Agent and tool-calling workflow |

---

# Project Structure

```text
DataCortex/
├── app/
│   ├── api/
│   │   └── routes/
│   ├── core/
│   ├── database/
│   │   └── seed/
│   ├── schemas/
│   └── services/
│
├── tests/
│
├── .github/
│   └── workflows/
│
├── .dockerignore
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── compose.yaml
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

# Tech Stack

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy

## Database

- PostgreSQL
- MySQL support
- SQL Server support
- Custom database adapters and dialects

## AI / LLM

- Ollama
- LLM-based Text-to-SQL
- Structured LLM output
- Function Calling
- Tool Calling
- AI Agent workflow
- RAG
- Sentence Transformers
- Semantic Embeddings
- Entity Resolution

## Testing & Code Quality

- pytest
- Ruff
- pre-commit
- GitHub Actions

## Infrastructure

- Docker
- Docker Compose

---

# Testing

The project uses automated tests across the database, SQL, AI, security, and abstraction layers.

Current test suite:

```text
141 passed
```

Coverage areas include:

- Database connectivity
- Schema discovery
- Database seeding
- SQL execution
- Query API
- SQL validation
- Schema-aware validation
- LLM integration
- Text-to-SQL
- AI query pipeline
- SQL cleaning
- Natural-language answer generation
- Tool calling
- AI agent workflow
- RAG
- Embeddings
- Entity resolution
- Database abstraction
- Database security

Run all tests:

```bash
pytest
```

## Testing Strategy

- Unit tests for isolated components
- Mocked LLM interactions where appropriate
- Database-backed integration tests
- Tests for database adapters and dialects
- Security-focused tests
- API tests

---

# Code Quality

```bash
pre-commit run --all-files
```

The project uses:

- **Ruff** for linting and formatting
- **pre-commit** for repository-level checks
- **GitHub Actions** for CI

---

# Docker

DataCortex provides Docker Compose configuration for the application and PostgreSQL infrastructure.

```text
Docker Compose
      │
      ├── datacortex_api
      │       │
      │       └── FastAPI
      │
      └── datacortex_db
              │
              └── PostgreSQL
```

Build the API image:

```bash
docker compose build api
```

Start the services:

```bash
docker compose up -d
```

Check service status:

```bash
docker compose ps
```

View API logs:

```bash
docker compose logs api
```

Stop the services:

```bash
docker compose down
```

PostgreSQL data is persisted through a Docker volume.

---

# Quick Start

## Prerequisites

- Python 3.14+
- Docker
- Docker Compose
- Ollama

## 1. Clone

```bash
git clone git@github.com:MotaharehFallah/DataCortex.git
cd DataCortex
```

## 2. Create the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

```bash
cp .env.example .env
```

Configure the database and local LLM settings in `.env`.

Do not commit `.env` or other files containing secrets.

## 5. Start the services

```bash
docker compose up -d
```

## 6. Check the API

```bash
curl http://localhost:8000/health
```

Open:

```text
http://localhost:8000/docs
```

---

# Local Development

For local Python development:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

When running the API outside Docker, configure the database and Ollama connection settings to point to services accessible from the host environment.

---

# Development Workflow

The project is developed feature-by-feature using isolated Git branches.

```text
Feature
   │
   ▼
Implementation
   │
   ▼
Tests
   │
   ▼
Ruff / Pre-commit
   │
   ▼
Git Commit
   │
   ▼
Git Push
```

---

# Roadmap

- [ ] Authentication and authorization
- [ ] Query result caching
- [ ] Streaming responses
- [ ] Additional database adapters
- [ ] Web UI
- [ ] BI integration

---

# Project Goal

DataCortex is a practical exploration of combining:

- Python backend engineering
- Relational databases
- LLMs
- Text-to-SQL
- AI agents
- RAG
- Embeddings
- Entity resolution
- Database abstraction
- Secure SQL execution

into a single backend-oriented AI system.

The goal is not to treat the LLM as an isolated feature, but to demonstrate how AI capabilities can be integrated into a **structured, testable, and security-conscious backend architecture**.

---

# License

MIT — see [LICENSE](LICENSE) for details.
