# thisKB

thisKB is a personal knowledge base application that allows you to manage documents, parse their contents, and search through them efficiently using both traditional text search and semantic vector search.

## Overview

thisKB enables users to upload and store documents, parse them for meaningful content, and then perform advanced searches and tasks. It provides a simple interface for document management with powerful search capabilities under the hood.

## Features

- **Document Upload**: Upload documents through UI and API
- **Document Parsing**: Automatically extract meaningful content from various document formats
- **Semantic Search**: Search documents using both text-based and semantic vector search
- **Multi-lingual Support**: Process and search documents in multiple languages
- **Chat Interface**: Interact with your knowledge base conversationally

## Tech Stack

- **Backend**: Django with Pydantic AI
- **Frontend**: HTMX + UIkit for a responsive interface
- **Databases**:
  - **PostgreSQL/ParadeDB** for data storage with pg_search and pgvector
- **Processing**:
  - **Celery + Redis** for task management and caching
  - **Extractous** (Rust-based), **Marker** (PDF), and **Magika** for file processing
- **Embeddings**:
  - **Jina Embeddings v3** (1024 dimensions, multilingual)
  - **OpenAI text-embedding-3-small** (1536 dimensions)
- **Chunking**: Chonkie for semantic chunking (and with double-pass merging)
- **Web Scraping**: crawl4ai, Jina Reader API/LLM
- **Storage**: S3/MinIO for document storage

## Basic Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/thiskb.git
   cd thiskb
   ```

2. Set up a virtual environment and install dependencies with uv:

   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

3. Set up environment variables in `.env`:

   ```env
   DATABASE_URL=postgres://user:password@localhost/thiskb
   REDIS_URL=redis://localhost:6379
   S3_BUCKET=thiskb
   S3_ENDPOINT=http://localhost:9000
   S3_ACCESS_KEY=minioadmin
   S3_SECRET_KEY=minioadmin
   ```

4. Run migrations:

   ```bash
   python manage.py migrate
   ```

5. Start the development server:

   ```bash
   python manage.py runserver
   ```

6. In a separate terminal, start Celery worker:

   ```bash
   celery -A thiskb worker --loglevel=info
   ```

## Installation with Docker (docker compose)

*[To be added]*

## Development

### Running Tests

```bash
python manage.py test
```

### Code Formatting

```bash
ruff format .
```

## API Documentation

API documentation is available at `/api/docs` when the server is running.

## Deployment

*[To be added]*

## Contributing

*[To be added]*

## License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for more information.