# Comask · marketing site

Standalone Next.js marketing site for Comask. Lives separately from the
product frontend so it can be deployed to its own host (Cloud Run) without
dragging the auth/backend along.

## Local dev

```bash
cd marketing
npm install --legacy-peer-deps
npm run dev
# → http://localhost:3002
```

## Local container

```bash
cd marketing
docker compose up --build
# → http://localhost:3002
```

## Deploy (Cloud Run)

The Dockerfile produces a Next.js standalone build that listens on `$PORT`
(defaults to 3002 locally; Cloud Run injects 8080 — Next.js standalone
respects the `PORT` env var, so override it on the service).

```bash
gcloud run deploy comask-marketing \
  --source . \
  --region us-central1 \
  --project epesya \
  --allow-unauthenticated \
  --port 3002
```
