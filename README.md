# Berlin AI Chatbot Platform

AI lead generation and customer-support platform for SMB websites.

## What It Does

- Creates one company workspace per signed-in business owner
- Generates a unique widget key for every company automatically
- Exposes a public chatbot route at `/widget/{company.widget_key}`
- Answers visitor questions from uploaded knowledge, pasted HTML, and scraped website content
- Captures leads and stores conversation history
- Gives the business owner a dashboard for leads, knowledge, analytics, privacy cleanup, and account deletion

## Stack

### Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Sentence Transformers
- Groq

### Frontend

- Next.js App Router
- TypeScript
- Tailwind CSS
- Clerk

## Local Development

### Backend

```powershell
cd apps\api
.venv\Scripts\activate
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

The local backend defaults to:

```text
postgresql+psycopg://chatbot:chatbot@localhost:5432/chatbot_db
```

If you use Docker for Postgres:

```powershell
docker compose up -d postgres
```

### Frontend

```powershell
cd apps\web
npm install
npm run dev
```

## Environment Files

### Backend

Use [apps/api/.env.example](D:/AI-CHAT-BOTS/berlin-ai-chatbot-platform-clean/apps/api/.env.example:1) as the template.

Required for normal local chat:

- `DATABASE_URL`
- `GROQ_API_KEY`

### Frontend

Use [apps/web/.env.example](D:/AI-CHAT-BOTS/berlin-ai-chatbot-platform-clean/apps/web/.env.example:1) as the template.

Required:

- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`

## Current Product Flow

1. User signs in with Clerk.
2. User creates a company in the dashboard.
3. Backend stores the company and auto-generates `widget_key`.
4. User adds knowledge by:
   - manual entry
   - pasted HTML
   - document upload
   - website scraping
5. Public chatbot is shared via `/widget/{company.widget_key}`.
6. Dashboard shows analytics, leads, knowledge, and conversations.

## Deployment

See [DEPLOYMENT.md](D:/AI-CHAT-BOTS/berlin-ai-chatbot-platform-clean/DEPLOYMENT.md:1).
