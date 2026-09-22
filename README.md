# DataCortex

DataCortex is an AI-powered database query system that allows users to interact with relational databases using natural language.

Instead of writing SQL manually, users can ask questions such as:

> "Show me total sales"

DataCortex converts the natural-language request into SQL, validates the generated query against the database schema and security policies, executes it through a database abstraction layer, and returns the result as a natural-language answer.

The project is designed with **clean architecture principles and separation of concerns**, with independent layers for API handling, AI services, SQL processing, database access, validation, and security.

## Key Capabilities

* Natural language to SQL
* Schema-aware SQL generation
* SQL cleaning and validation
* Database query security and row limits
* Database-agnostic architecture
* PostgreSQL, MySQL, and SQL Server dialect support
* LLM integration
* Structured LLM output
* Function and tool calling
* AI agent workflow
* RAG-based knowledge retrieval
* Semantic search with embeddings
* Entity resolution
* Natural-language answer generation
* Automated testing
* CI workflow

## Architecture

DataCortex separates API handling, AI services, SQL processing, database access, validation, and security.

### Main Request Flow

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
Natural Language Answer
```

### AI Components

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

### Architectural Principles

* Separation of concerns
* Service-oriented business logic
* Database abstraction through adapters and dialects
* Database-specific behavior isolated behind abstractions
* Independent validation and security policies
* Schema-aware SQL processing
* Testable components
* Clear separation between API, AI, and database layers

## Core AI Pipeline

DataCortex combines several AI capabilities into a single workflow:

```text
Natural Language
       │
       ▼
   LLM Processing
       │
       ▼
   Text-to-SQL
       │
       ▼
 SQL Cleaning & Validation
       │
       ▼
 Schema Validation
       │
       ▼
 Secure SQL Execution
       │
       ▼
 Query Result
       │
       ▼
 Natural Language Answer
```

Additional AI capabilities include:

```text
AI Agent
   │
   ├── Function Calling
   ├── Tool Calling
   ├── RAG
   ├── Embeddings
   └── Entity Resolution
```

## Database Architecture

Database-specific behavior is isolated behind a common abstraction:

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

This allows database-specific behavior such as:

* SQL placeholders
* Query limits
* Database-specific row limiting syntax
* Database selection

to remain isolated from the higher-level query execution logic.

## Security

DataCortex applies multiple layers of protection before executing generated SQL.

```text
Generated SQL
     │
     ▼
SQL Validation
     │
     ▼
Schema Validation
     │
     ▼
Database Security Policy
     │
     ▼
Database-specific Row Limit
     │
     ▼
SQL Execution
```

The security layer includes:

* SELECT-only query validation
* Multiple-statement protection
* Dangerous SQL pattern validation
* Schema-aware validation
* Database-side row limits
* Post-execution row-count validation

The default maximum result size is **1000 rows**.

## RAG and Semantic Search

DataCortex includes a retrieval pipeline for knowledge-aware responses:

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

The embedding pipeline uses `sentence-transformers` and supports semantic retrieval over stored knowledge.

## Project Structure

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
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── compose.yaml
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Tech Stack

### Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy

### Database

* PostgreSQL
* MySQL support
* SQL Server support
* Database abstraction through custom adapters and dialects

### AI / LLM

* Ollama
* LLM-based Text-to-SQL
* Structured LLM output
* Function Calling
* Tool Calling
* AI Agent workflow
* RAG
* Sentence Transformers
* Semantic Embeddings
* Entity Resolution

### Testing & Code Quality

* pytest
* Ruff
* pre-commit
* GitHub Actions

### Infrastructure

* Docker
* Docker Compose

## Testing

The project includes automated tests covering:

* Database connectivity
* Schema discovery
* Database seeding
* SQL execution
* Query API
* SQL validation
* Schema-aware validation
* Text-to-SQL
* LLM integration
* AI query pipeline
* Natural-language answer generation
* Tool calling
* AI agent workflow
* RAG
* Embeddings
* Entity resolution
* Database abstraction
* Database security

Run the complete test suite with:

```bash
pytest
```

Current test status:

```text
141 passed
```

## Code Quality

Run all pre-commit checks with:

```bash
pre-commit run --all-files
```

The project uses Ruff for linting and formatting and pre-commit hooks for repository-level checks.

## Running the Project

### 1. Clone the repository

```bash
git clone git@github.com:MotaharehFallah/DataCortex.git
cd DataCortex
```

### 2. Create and activate the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on `.env.example` and configure the required database and LLM settings.

### 5. Start infrastructure

```bash
docker compose up -d
```

### 6. Start the FastAPI application

```bash
uvicorn app.main:app --reload
```

The API documentation is available through FastAPI's generated OpenAPI interface.

## Development Workflow

The project is developed feature-by-feature with isolated Git branches.

Each feature follows:

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

## Project Goal

DataCortex was built as a practical exploration of combining **Python backend engineering, relational databases, LLMs, SQL generation, AI agents, RAG, embeddings, and secure database execution** into a single production-oriented architecture.

The project focuses on applying AI capabilities to a backend engineering problem rather than treating the LLM as an isolated component.
