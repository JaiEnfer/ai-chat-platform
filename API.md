# API Documentation

## Health

GET /api/health

## Companies

POST /api/companies

GET /api/companies/{company_id}

## Leads

POST /api/leads

GET /api/companies/{company_id}/leads

## Knowledge Items

POST /api/knowledge-items

GET /api/companies/{company_id}/knowledge-items

## Chat

POST /api/chat

Example:

```json
{
  "company_id": 1,
  "visitor_id": "visitor-123",
  "message": "Can I book an appointment?"
}
```

## Analytics

GET /api/companies/{company_id}/analytics
