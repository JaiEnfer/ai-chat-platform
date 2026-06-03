# Berlin AI Chatbot Platform

## Overview

AI Lead Generation & Customer Support Platform for SMBs.

Core Features:
- Multi-company architecture
- Chat widget
- Lead capture
- Knowledge base
- Conversation logging
- Analytics dashboard

## Tech Stack

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic

### Frontend
- Next.js
- TypeScript
- Tailwind CSS

## Run Backend

```powershell
cd apps\api
.venv\Scripts\activate
uvicorn app.main:app --reload
```

### Local Database

Start Docker Desktop, then run:

```powershell
docker compose up -d postgres
```

The local API expects:

```text
postgresql+psycopg://chatbot:chatbot@localhost:5432/chatbot_db
```

If you need tables locally, run:

```powershell
cd apps\api
.venv\Scripts\activate
alembic upgrade head
```

## Run Frontend

```powershell
cd apps\web
npm run dev
```
