# Deployment Guide

## Backend Deployment

Recommended:
- Railway
- Render
- DigitalOcean
- AWS

### Railway Setup

For this monorepo, configure the API Railway service with:
- Root Directory: `apps/api`
- Healthcheck Path: `/health`

Add a PostgreSQL service in the same Railway project, then expose one of:
- `DATABASE_URL`
- or `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`

Do not set `DATABASE_URL` to `localhost` or `127.0.0.1` on Railway.

## Frontend Deployment

Recommended:
- Vercel

## Environment Variables

### Backend

DATABASE_URL=

Optional alternative:
- PGHOST=
- PGPORT=
- PGUSER=
- PGPASSWORD=
- PGDATABASE=

### Frontend

NEXT_PUBLIC_API_BASE_URL=
NEXT_PUBLIC_WIDGET_KEY=
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=

## Production Notes

- Enable HTTPS
- Add authentication
- Use managed PostgreSQL
- Add monitoring
- Add backups
