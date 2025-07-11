# Travel Bureau

This project contains a FastAPI backend and a Next.js frontend.

## Backend

1. Create a virtual environment and activate it.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Optionally, set `DATABASE_URL` if you are not using the default local PostgreSQL database.
4. Start the API server from the project root:
   ```bash
   uvicorn backend.app:app --reload
   ```

## Frontend

Navigate to the `frontend` directory and start the development server:

```bash
cd frontend
npm install
npm run dev
```
