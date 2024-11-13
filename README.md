# thisKB

thisKB is a personal knowledge base application that allows you to manage documents, parse their contents, and search through them efficiently using both traditional text search and semantic vector search.

## Overview

thisKB enables users to upload and store documents, parse them for meaningful content, and then perform advanced searches.

It integrates with **PostgreSQL** for user and metadata management, and **ParadeDB** for storing parsed documents and embeddings, providing fast and scalable search capabilities.

## Features

- **Document Upload**: Upload documents and manage metadata.
- **Document Parsing**: Automatically parse content from uploaded documents.
- **Semantic Search**: Search documents using both text-based (BM25) and semantic (vector) search techniques.
- **Scalability**: Built to scale with multi-tenant support.

## Tech Stack

- **Backend**: Rust, powered by the **loco.rs** MVC framework.
- **Databases**:
  - **PostgreSQL** for user data and metadata.
  - **ParadeDB** for storing parsed documents and embeddings (with **pgvector** for vector search).
- **Search**: **BM25** for text search, **pgvector** for semantic search.
- **(temp) File Storage**: **AWS S3** (or **MinIO**) for document storage.
- **Caching**: **Redis** for caching search results.
- **Document Parsing**: **unstructured.io** for extracting meaningful content from documents.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/thiskb.git
   cd thiskb
   ```

2. Install dependencies:

   ```bash
   cargo build
   ```

3. Set up the environment variables in `.env`:

   ```env
   DATABASE_URL=postgres://user:password@localhost/thiskb
   PARADEDB_URL=paradedb://user:password@localhost/thiskb
   REDIS_URL=redis://localhost:6379
   ```

4. Run migrations:

   ```bash
   cargo migrate
   ```

5. Start the app:
   ```bash
   cargo run
   ```

## License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for more information.
