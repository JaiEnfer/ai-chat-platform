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

## Run Frontend

```powershell
cd apps\web
npm run dev
```
