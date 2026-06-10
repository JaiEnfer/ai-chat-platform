# Database Documentation

## Overview

The backend uses PostgreSQL with SQLAlchemy models and Alembic migrations.

Core business data is grouped by `company_id`.

## Tables

### `companies`

Stores one company workspace for each Clerk owner user.

Important fields:

- `id`
- `owner_user_id`
- `widget_key`
- `name`
- `website`
- `created_at`
- `updated_at`

Notes:

- `widget_key` is generated automatically by the backend
- it is the public identifier used by the chat widget route and chat API

### `leads`

Stores lead submissions captured by the widget.

Important fields:

- `id`
- `company_id`
- `name`
- `email`
- `phone`
- `message`
- `status`
- `created_at`
- `updated_at`

### `knowledge_items`

Stores readable business knowledge added through the dashboard.

Sources include:

- manual entry
- pasted HTML
- uploaded documents
- scraped websites

Important fields:

- `id`
- `company_id`
- `title`
- `content`
- `created_at`
- `updated_at`

### `knowledge_chunks`

Stores chunked retrieval records derived from knowledge items and website imports.

Important fields:

- `id`
- `company_id`
- `source`
- `content`
- `embedding`
- `created_at`
- `updated_at`

Notes:

- `embedding` is stored as a Postgres float array
- retrieval is currently done in Python, not with pgvector

### `conversation_messages`

Stores visitor chat history and bot answers.

Important fields:

- `id`
- `company_id`
- `visitor_id`
- `user_message`
- `bot_answer`
- `should_collect_lead`
- `created_at`
- `updated_at`

## Relationships

Company
- has many leads
- has many knowledge items
- has many knowledge chunks
- has many conversation messages

## Data Lifecycle

- deleting a knowledge item also deletes its related chunks
- deleting a company removes its leads, conversations, knowledge items, and knowledge chunks
- clearing leads or conversations operates per company
