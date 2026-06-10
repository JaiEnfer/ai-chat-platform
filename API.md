# API Documentation

Base prefix: `/api`

## Health

- `GET /api/health`

## Companies

- `POST /api/companies`
- `GET /api/companies/{company_id}`
- `GET /api/users/{owner_user_id}/company`
- `DELETE /api/companies/{company_id}`

## Leads

- `POST /api/leads`
- `GET /api/companies/{company_id}/leads`
- `PATCH /api/leads/{lead_id}/status`
- `DELETE /api/leads/{lead_id}`
- `DELETE /api/companies/{company_id}/leads`

Lead creation example:

```json
{
  "widget_key": "your-company-widget-key",
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "+49 123456789",
  "message": "Please contact me about pricing."
}
```

## Knowledge

- `POST /api/knowledge-items`
- `GET /api/companies/{company_id}/knowledge-items`
- `DELETE /api/knowledge-items/{item_id}`
- `POST /api/companies/{company_id}/knowledge-html`
- `POST /api/companies/{company_id}/knowledge-files`
- `POST /api/companies/{company_id}/scrape-website`

Chat request example:

```json
{
  "widget_key": "your-company-widget-key",
  "visitor_id": "visitor-123",
  "message": "Can I book an appointment?"
}
```

## Chat

- `POST /api/chat`

Response shape:

```json
{
  "answer": "Yes, we can help with that.",
  "should_collect_lead": true
}
```

## Conversations

- `GET /api/companies/{company_id}/conversation-messages`
- `GET /api/companies/{company_id}/visitors/{visitor_id}/conversation-messages`
- `DELETE /api/companies/{company_id}/conversation-messages`

## Analytics

- `GET /api/companies/{company_id}/analytics`
