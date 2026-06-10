# Product Roadmap

## Current State

- Clerk sign-in
- company creation
- backend-generated widget keys
- public widget route
- Groq-backed answer generation
- retrieval from:
  - manual knowledge
  - HTML imports
  - uploaded documents
  - scraped websites
- lead capture
- conversation logging
- analytics dashboard
- privacy cleanup and company data deletion

## Next Priorities

### Security

- add server-side authorization for sensitive API routes
- verify ownership on company-scoped mutations
- add stronger production request validation

### Product

- per-conversation deletion
- copy widget link action
- clearer success/error toasts in dashboard
- better knowledge source previews

### AI Quality

- better reranking for support answers
- source-aware answer grounding
- more robust multi-page scraping heuristics
- optional answer citations for business owners

### Platform

- deployment smoke tests
- structured backend logging
- background jobs for large imports
- usage monitoring and rate limiting

### Commercial Readiness

- multi-user teams per company
- billing
- white-label widget branding
- CRM and notification integrations
