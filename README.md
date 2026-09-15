# IntakeGuard

IntakeGuard is a deterministic enterprise data intake and de-identification guardrail. It profiles uploaded CSV datasets, detects and redacts supported sensitive values, validates transformed output, and returns an auditable `READY` or `BLOCKED` ingestion decision.

The prototype uses a Python/FastAPI backend and a React/TypeScript/Vite dashboard. It does not persist uploaded data and does not use LLMs.

## Requirements

- Python 3.11+
- Node.js 20+
- npm

## Run the backend

```powershell
cd backend
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Interactive documentation is available at `http://127.0.0.1:8000/docs`.

## Run the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. To use another API location, copy `.env.example` to `.env` and change `VITE_API_BASE_URL`.

## Demo flows

- **Dirty Manufacturing Dataset** demonstrates successful PII redaction followed by a `BLOCKED` decision due to a missing machine identifier and duplicate work-order identifier.
- **Clean Manufacturing Dataset** demonstrates successful PII redaction and a `READY` decision.
- **Upload CSV** accepts a custom `.csv` file up to 5 MB.

## Tests and build

```powershell
cd backend
python -m pytest -q

cd ..\frontend
npm run build
```

## API endpoints

- `GET /health`
- `POST /api/intake/profile`
- `POST /api/intake/redact`
- `POST /api/intake/validate`

## Deployment

The frontend and backend are deployed as separate services. No deployment credentials or final service URLs belong in source control.

### Backend — Railway

1. Push the repository to GitHub.
2. Create a Railway project and choose **Deploy from GitHub repo**.
3. Select the IntakeGuard repository.
4. Set the service **Root Directory** to `backend`.
5. Railway will install `requirements.txt`. The committed `railway.toml` starts the service with:

   ```text
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

6. Add this Railway service variable, initially using the intended Vercel domain:

   ```text
   CORS_ALLOWED_ORIGINS=https://<vercel-domain>
   ```

   Multiple explicit origins may be comma-separated. Never use `*`.

7. Deploy the service, open **Settings → Networking**, and generate a public domain.
8. Verify `https://<railway-domain>/health` returns HTTP 200 and the IntakeGuard health payload.
9. Record the final public Railway URL for the frontend configuration.

The Railway health-check path is `/health`. `PORT` is supplied automatically by Railway and should not be set manually.

### Frontend — Vercel

1. Import the same GitHub repository into Vercel.
2. Set the project **Root Directory** to `frontend`.
3. Select the **Vite** framework preset.
4. Use `npm install` as the install command (the detected default).
5. Set the build command to `npm run build`.
6. Set the output directory to `dist`.
7. Add this environment variable for Production and any Preview environments that should use the backend:

   ```text
   VITE_API_BASE_URL=https://<railway-domain>
   ```

8. Deploy the frontend.

No `vercel.json` is required because IntakeGuard is a routing-free static Vite application.

### Final CORS update

After Vercel assigns the final production domain, set the Railway variable to the exact origin:

```text
CORS_ALLOWED_ORIGINS=https://<final-vercel-domain>
```

Redeploy or restart the Railway service if required so the updated environment reaches the running process. Add other explicit origins as comma-separated values only when those deployments must call the API.

### Recommended deployment order

1. Prepare and push the repository.
2. Deploy the Railway backend first.
3. Confirm the Railway `/health` endpoint.
4. Copy the Railway public URL.
5. Configure Vercel `VITE_API_BASE_URL` with that URL.
6. Deploy the Vercel frontend.
7. Copy the final Vercel URL.
8. Set Railway `CORS_ALLOWED_ORIGINS` to the final Vercel origin.
9. Redeploy or restart Railway if required.
10. Perform the complete production E2E verification below.

### Production E2E checklist

- [ ] Frontend loads from Vercel
- [ ] Railway `/health` returns 200
- [ ] Dirty Manufacturing Dataset returns `BLOCKED`
- [ ] Missing `machine_id` appears
- [ ] Duplicate `work_order_id` appears
- [ ] Duplicate-row warning appears
- [ ] Clean Manufacturing Dataset returns `READY`
- [ ] Sensitive findings are greater than zero
- [ ] Redactions applied are greater than zero
- [ ] Residual PII is zero
- [ ] Redaction Preview renders
- [ ] Audit & Transformation Record renders
- [ ] Manual CSV upload works
- [ ] Invalid-file handling works
- [ ] Browser console has no CORS errors
- [ ] No localhost URLs appear in production requests
