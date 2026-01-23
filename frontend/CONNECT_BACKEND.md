# Connecting Frontend to Backend

## Setup

1. **Create `.env.local` file** in the `frontend/` directory:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

2. **Start the backend server** (in `backend/` directory):
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Start the frontend** (in `frontend/` directory):
   ```bash
   npm run dev
   ```

## API Integration

The frontend is now connected to the backend through:

- **API Client**: `frontend/lib/api.ts`
  - `submitQuery()` - Sends queries to `/api/queries`
  - `healthCheck()` - Checks backend health

- **Chat Interface**: `frontend/components/ChatInterface.tsx`
  - Calls `submitQuery()` when user submits a question
  - Displays real responses from the backend
  - Shows processing pipeline visualization

## API Endpoints

- **POST** `/api/queries` - Submit a query
  - Request: `{ question: string, location: string }`
  - Response: `{ answer: string, citations: [], confidence: string, ... }`

- **GET** `/health` - Health check
  - Response: `{ status: "healthy" }`

## CORS

The backend is configured to allow all origins in development. For production, update CORS settings in `backend/app/main.py`.

## Testing

1. Open the frontend at `http://localhost:3000`
2. Select Colorado from the dropdown
3. Ask a question about energy regulations
4. The frontend will call the backend API and display the response

## Troubleshooting

- **Connection refused**: Make sure the backend is running on port 8000
- **CORS errors**: Check that CORS middleware is enabled in backend
- **404 errors**: Verify the API URL in `.env.local` matches your backend URL

