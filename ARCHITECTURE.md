# System Architecture

## High-Level Flow

Visitor
- opens a public widget page at `/widget/{company.widget_key}`
- sends a question

Next.js widget
- posts chat request to FastAPI

FastAPI backend
- resolves the company from `widget_key`
- retrieves relevant knowledge chunks
- asks Groq for a natural answer when possible
- falls back to local answer synthesis when needed
- stores the conversation

PostgreSQL
- stores companies, leads, knowledge, chunks, and conversations

## Frontend Areas

### Public Widget

- route: `/widget/[widgetKey]`
- used by public visitors
- submits chat and lead capture by `widget_key`

### Marketing / Signed-In Home

- route: `/`
- signed-in users can reach their dashboard
- signed-in users can also see their company-aware testing flow

### Dashboard

- route: `/dashboard`
- protected by Clerk
- manages:
  - company setup
  - website scrape import
  - manual knowledge
  - HTML knowledge
  - document upload
  - leads
  - conversation history
  - privacy cleanup

## Backend Areas

### Companies API

- creates and looks up company records
- auto-generates `widget_key`
- deletes company-owned data on account deletion

### Chat API

- resolves company from `widget_key`
- uses retrieval + LLM answer generation
- stores `conversation_messages`

### Knowledge APIs

- manual knowledge entry
- HTML import
- file import
- website scrape import

### Lead APIs

- create, list, update status
- delete one lead or clear all leads for a company

### Conversation APIs

- list per company
- list per visitor
- clear company conversation history

## Retrieval Pipeline

1. Normalize input
2. Generate embedding for query
3. Compare against stored `knowledge_chunks`
4. Rank by keyword overlap and cosine similarity
5. Send the best chunks to Groq
6. Fall back to a local natural summary if Groq is unavailable
