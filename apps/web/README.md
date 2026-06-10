# Web App

Next.js frontend for the Berlin AI Chatbot Platform.

## Main Routes

- `/`
  marketing page plus signed-in company-aware entry point
- `/dashboard`
  protected business dashboard
- `/widget/[widgetKey]`
  public chatbot route for a company

## Environment Variables

Use [apps/web/.env.example](D:/AI-CHAT-BOTS/berlin-ai-chatbot-platform-clean/apps/web/.env.example:1).

Required:

- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`

## Run Locally

```powershell
cd apps\web
npm install
npm run dev
```

## Build

```powershell
npm run build
```

## Notes

- the dashboard is protected through Clerk route protection
- the public widget uses the backend-generated company widget key
- `NEXT_PUBLIC_WIDGET_KEY` is no longer part of the normal flow
