# DataCortex

**DataCortex** is an AI-powered natural-language-to-SQL backend that allows users to query relational databases using plain English.

The project combines **FastAPI, PostgreSQL, SQLAlchemy, LLMs, SQL validation, business semantics, Docker, and automated testing** to build a controlled AI-to-database workflow.

Instead of allowing an LLM to directly access a database, DataCortex places validation, schema awareness, business rules, and execution boundaries between the LLM and the database.

---

## Architecture

DataCortex follows a layered architecture inspired by **Clean Architecture** principles.

The system separates API handling, application services, AI/LLM integration, business semantics, database access, validation, and result formatting.

```text
                    ┌──────────────────────┐
                    │      FastAPI API     │
                    │   HTTP / Validation  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Application Layer  │
                    │    AIQueryService    │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
       │ LLM / Agent │  │   Business   │  │   Answer     │
       │    Layer    │  │   Semantics  │  │  Formatting  │
       └──────┬──────┘  └──────────────┘  └──────────────┘
              │
              ▼
       ┌──────────────────────┐
       │ SQL Cleaner          │
       │ SQL Validator        │
       │ Schema Validation    │
       │ SQL Repair           │
       └──────────┬───────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │    Database Layer    │
       │ Schema Discovery     │
       │ SQL Execution        │
       │ Database Adapters    │
       └──────────┬───────────┘
                  │
                  ▼
              PostgreSQL
```

### Main Layers

**API Layer**

Handles HTTP requests, validation, and API responses using FastAPI.

**Application Layer**

Coordinates the complete natural-language-to-database workflow through `AIQueryService`.

**AI Layer**

Handles LLM interaction and the experimental agent/tool-calling capabilities.

**Business Semantic Layer**

Defines domain-specific meanings that cannot safely be inferred from database structure alone.

Examples include:

* `total_sales`
* `product_sales`
* `order_subtotal`
* `order_total`

**Database Layer**

Responsible for:

* schema discovery
* SQL execution
* SQL validation
* database adapters
* database-specific behavior

**Formatting Layer**

Converts database results into deterministic, human-readable responses.

**Infrastructure**

Docker, PostgreSQL, Ollama, configuration, and local development infrastructure.

This separation keeps business logic independent from HTTP handlers and makes individual components easier to test and replace.

---

## Testing & Code Quality

Testing is a core part of DataCortex.

The current test suite contains:

```text
143 passed
1 dependency warning
```

The tests cover multiple layers of the application, including:

* API endpoints
* SQL generation prompts
* SQL validation
* SQL security rules
* SQL repair
* database schema discovery
* database execution
* business semantic rules
* result formatting
* answer generation
* integration-oriented database behavior

Example:

```text
pytest -q

143 passed, 1 warning
```

The project also uses **Ruff** and **pre-commit** for code quality.

```text
Ruff checks       ✓
Ruff formatting   ✓
Pre-commit hooks  ✓
```

The goal is to keep the AI workflow testable and deterministic wherever possible, especially around SQL validation, business rules, database execution, and result formatting.

---

## Core Flow

A user can ask a question such as:

```text
What are the top 5 products by total sales?
```

The request follows this pipeline:

```text
User Question
      │
      ▼
   FastAPI
      │
      ▼
 Schema Discovery
      │
      ▼
Business Semantics
      │
      ▼
    LLM
      │
      ▼
 Text-to-SQL
      │
      ▼
 SQL Cleaning
      │
      ▼
 SQL Validation
      │
      ├── Invalid ──► SQL Repair ──► Validation
      │
      ▼
 SQL Execution
      │
      ▼
 PostgreSQL
      │
      ▼
Deterministic Result Formatting
      │
      ▼
    API Response
```

The LLM generates SQL, but generated SQL is treated as **untrusted input**.

The application validates the query before execution.

---

## AI Capabilities

### 1. Natural Language to SQL

DataCortex converts natural-language questions into SQL queries.

Example:

```text
User:
What are the top 5 products by total sales?
```

The LLM can generate:

```sql
SELECT
    p.name,
    SUM(oi.line_total) AS total_sales
FROM products p
JOIN order_items oi
    ON p.id = oi.product_id
GROUP BY p.name
ORDER BY total_sales DESC
LIMIT 5;
```

---

### 2. Schema Discovery

The LLM receives information about the available database structure instead of being allowed to assume arbitrary tables or columns.

Example schema information includes:

```text
products
- id
- name
- price
- cost
- category_id

order_items
- id
- order_id
- product_id
- quantity
- unit_price
- discount_amount
- line_total

orders
- id
- customer_id
- status
- ordered_at
- subtotal
- tax_amount
- total_amount
```

This reduces hallucinated tables and columns during SQL generation.

---

## Business Semantic Layer

Database schemas describe **how data is stored**, but they do not necessarily describe **what business concepts mean**.

For example, the database contains:

```text
products.price
order_items.unit_price
order_items.line_total
orders.subtotal
orders.total_amount
```

A question such as:

```text
What are the total sales?
```

cannot safely be answered only from column names.

DataCortex therefore defines explicit business semantics.

### Example

```text
total_sales
    = SUM(order_items.line_total)
```

The system explicitly prevents the LLM from interpreting total sales as:

```text
SUM(products.price)
```

or:

```text
SUM(orders.total_amount)
```

when the business definition requires order-item sales.

This semantic layer provides domain knowledge that sits between database schema discovery and SQL generation.

---

## SQL Validation

LLM-generated SQL is treated as untrusted input.

Before execution, DataCortex validates the generated query.

The validation layer checks that the query:

* is a `SELECT` statement
* does not contain destructive SQL operations
* uses allowed tables
* uses allowed columns
* follows database schema constraints
* does not violate configured SQL safety rules

The system rejects statements such as:

```sql
DROP TABLE products;
```

```sql
DELETE FROM orders;
```

```sql
UPDATE products SET price = 0;
```

The database should never rely on the LLM to enforce its own security boundaries.

---

## SQL Repair

If generated SQL fails validation, DataCortex can send the validation error back to the LLM through a dedicated SQL repair prompt.

```text
Generated SQL
     │
     ▼
 Validation
     │
     ├── Valid ───────► Execute
     │
     ▼
 Validation Error
     │
     ▼
 Repair Prompt
     │
     ▼
 LLM
     │
     ▼
 Corrected SQL
     │
     ▼
 Validation Again
```

The repaired query must pass validation before it can reach the database.

---

## Deterministic Answers

The final response is generated from the database result rather than asking the LLM to summarize arbitrary database output.

For example:

```text
1. User-friendly multimedia firmware — 31642.81
2. Enhanced didactic moratorium — 24842.32
3. Polarized needs-based Graphic Interface — 22509.07
4. Decentralized executive installation — 20229.52
5. Self-enabling uniform model — 18539.76
```

This keeps the final formatting predictable and reduces unnecessary LLM usage after the database query has already produced the authoritative result.

---

## Experimental Agent & Tool Calling

DataCortex also contains an experimental agent/tool-calling implementation.

The project includes the ability to represent database operations as tools and expose them to an LLM-based agent.

However, the main production query path currently uses:

```text
Natural Language
       ↓
Text-to-SQL
       ↓
Validation
       ↓
Execution
```

rather than depending on unreliable tool selection from a small local model.

Tool calling is therefore treated as an **experimental agent capability** and a foundation for future iterations.

---

## Local LLM

The current local development setup uses:

```text
Ollama
└── Qwen 2.5 Coder 1.5B
```

The local model is used for SQL generation and SQL repair.

The architecture keeps the LLM integration behind a service layer so that the model can be replaced without changing the rest of the application.

Possible future providers include:

* local models
* OpenAI-compatible APIs
* other hosted LLM providers

---

## Database Abstraction

DataCortex introduces a database adapter layer to avoid tightly coupling database-specific behavior to the application layer.

The current primary execution database is:

```text
PostgreSQL
```

The architecture also contains database-specific adapter concepts for future support of other relational databases such as:

```text
PostgreSQL
MySQL
SQL Server
```

The project does not currently claim complete end-to-end production support for every listed database.

The abstraction is intended to make database-specific SQL behavior replaceable without rewriting the application layer.

---

## RAG & Embeddings

The project includes the foundation for retrieval and semantic capabilities that can be used to improve AI-driven database interaction.

Potential use cases include:

* retrieving relevant schema information
* retrieving business definitions
* retrieving documentation
* grounding SQL generation with domain knowledge
* semantic matching of database entities

These capabilities are part of the project's broader AI architecture and are not required by the primary Text-to-SQL execution path.

---

## Entity Resolution

Entity resolution is another planned capability for handling natural-language references to database entities.

For example, a user might ask:

```text
Show sales for Apple.
```

while the database may contain:

```text
Apple Inc.
Apple Store
Apple Services
```

A future entity-resolution layer can determine which database entity the user actually means before generating SQL.

This is particularly useful when natural language and database naming conventions do not match exactly.

---

## Security Principles

DataCortex treats AI-generated SQL as untrusted input.

The security model is based on multiple layers:

```text
LLM Output
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
Database Execution
```

Important principles include:

* allow only intended SQL operations
* validate generated SQL before execution
* validate tables and columns against discovered schema
* avoid trusting LLM-generated identifiers
* keep database credentials outside source control
* use environment variables for configuration
* isolate infrastructure using Docker where appropriate

AI-generated code should never be considered safe simply because it was generated by an LLM.

---

## Project Structure

```text
DataCortex/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── query.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   ├── connection.py
│   │   ├── query.py
│   │   ├── schema.py
│   │   ├── semantics.py
│   │   └── sql_validator.py
│   │
│   ├── schemas/
│   │   └── ai_query.py
│   │
│   ├── services/
│   │   ├── agent.py
│   │   ├── ai_query.py
│   │   ├── answer.py
│   │   ├── llm.py
│   │   ├── result_formatter.py
│   │   ├── sql_cleaner.py
│   │   ├── sql_prompt.py
│   │   ├── sql_repair_prompt.py
│   │   └── tools.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   └── main.py
│
├── tests/
│   ├── ...
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── .dockerignore
├── .gitignore
└── README.md
```

---

## Example

### Request

```http
POST /ai/query
```

```json
{
  "question": "What are the top 5 products by total sales?"
}
```

### Generated SQL

```sql
SELECT
    p.name,
    SUM(oi.line_total) AS total_sales
FROM products p
JOIN order_items oi
    ON p.id = oi.product_id
GROUP BY p.name
ORDER BY total_sales DESC
LIMIT 5;
```

### Response

```json
{
  "question": "What are the top 5 products by total sales?",
  "sql": "SELECT p.name, SUM(oi.line_total) AS total_sales FROM products p JOIN order_items oi ON p.id = oi.product_id GROUP BY p.name ORDER BY total_sales DESC LIMIT 5;",
  "columns": [
    "name",
    "total_sales"
  ],
  "rows": [
    {
      "name": "User-friendly multimedia firmware",
      "total_sales": "31642.81"
    }
  ],
  "row_count": 5,
  "answer": "1. User-friendly multimedia firmware — 31642.81"
}
```

The response above is shortened for readability; the actual API returns all rows in the result set.

---

## Technology Stack

| Technology     | Purpose                     |
| -------------- | --------------------------- |
| Python         | Core application language   |
| FastAPI        | REST API                    |
| PostgreSQL     | Primary relational database |
| SQLAlchemy     | Database abstraction        |
| psycopg        | PostgreSQL driver           |
| Ollama         | Local LLM runtime           |
| Qwen 2.5 Coder | Local SQL generation model  |
| SQLGlot        | SQL parsing/analysis        |
| Pydantic       | Data validation             |
| Docker         | Containerization            |
| Pytest         | Automated testing           |
| Ruff           | Linting and formatting      |
| Pre-commit     | Code quality automation     |
| GitHub Actions | CI                          |

---

## Running Locally

### 1. Clone the repository

```bash
git clone git@github.com:MotaharehFallah/DataCortex.git
cd DataCortex
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on:

```text
.env.example
```

Do not commit secrets to Git.

### 5. Start PostgreSQL

Using Docker:

```bash
docker compose up -d db
```

### 6. Start Ollama

Make the local Ollama server available to the application:

```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

Then make sure the required model is available:

```bash
ollama list
```

### 7. Start the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Running with Docker

Build and start the services:

```bash
docker compose up --build
```

The application container runs the FastAPI service and connects to PostgreSQL through the Docker network.

The local LLM can be accessed through the host Ollama service when configured appropriately.

---

## Running Tests

Run the complete test suite:

```bash
pytest -q
```

Current result:

```text
143 passed, 1 warning
```

Run Ruff:

```bash
ruff check .
ruff format --check .
```

Run all pre-commit hooks:

```bash
pre-commit run --all-files
```

---

## CI

GitHub Actions runs automated quality checks for the project.

The CI workflow includes:

* dependency installation
* test execution
* linting
* formatting checks

This helps prevent broken code from being pushed without verification.

---

## Current Status

DataCortex currently demonstrates a complete AI-assisted database query workflow:

```text
Natural Language
       ↓
Schema Discovery
       ↓
Business Semantics
       ↓
LLM Text-to-SQL
       ↓
SQL Cleaning
       ↓
SQL Validation
       ↓
SQL Repair
       ↓
PostgreSQL Execution
       ↓
Deterministic Formatting
       ↓
API Response
```

The main workflow is implemented and tested.

The project also contains experimental foundations for:

* agent workflows
* tool calling
* RAG
* embeddings
* entity resolution
* database abstraction

These components are intentionally separated from the core execution path so that the main system remains predictable and testable.

---

## Roadmap

Future development may include:

* authentication and authorization
* query caching
* streaming responses
* richer database adapters
* improved entity resolution
* production-grade vector database integration
* advanced RAG workflows
* query observability and tracing
* query cost estimation
* rate limiting
* web-based analytics interface
* BI-oriented natural-language querying

---

## Engineering Goals

DataCortex is designed around several engineering principles:

* **AI should be constrained by application rules.**
* **LLM output should be treated as untrusted input.**
* **Business semantics should be explicit rather than inferred blindly.**
* **Database access should remain isolated behind application boundaries.**
* **AI components should be replaceable.**
* **Critical behavior should be covered by automated tests.**
* **Deterministic operations should not unnecessarily depend on an LLM.**

The project focuses on combining AI capabilities with conventional backend engineering practices rather than treating the LLM as the entire application.

---
