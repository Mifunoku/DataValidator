# 🚀 GCP Deployment Guide for Dataset Review App

This guide shows how to deploy your **Dataset Review App** on **Google Cloud Platform** using:
- React Frontend → Cloud Storage static website
- FastAPI Backend → Cloud Run
- Data storage → Firestore (for rows) and Cloud Storage (for files)

---

## 📦 1. Setup GCP Project

```bash
gcloud init
gcloud auth login
gcloud config set project PROJECT_ID
gcloud config set compute/region YOUR_REGION
```

✅ Enable APIs:
```bash
gcloud services enable run.googleapis.com firestore.googleapis.com storage.googleapis.com
```

---

## 🌐 2. Frontend Deployment (React)

### Build React app
```bash
cd frontend
npm install
npm run build
```

### Create Cloud Storage bucket for frontend
```bash
gsutil mb -p YOUR_PROJECT_ID -l YOUR_REGION gs://your-frontend-bucket-name
```

### Set static website configuration
```bash
gsutil web set -m index.html -e 404.html gs://your-frontend-bucket-name
```

### Upload build
```bash
gsutil rsync -R ./dist gs://your-frontend-bucket-name
```

✅ (Optional) Set public read access for static hosting.

---

## 🐍 3. Backend Deployment (FastAPI)

### Build and deploy Cloud Run

Create Dockerfile (already done):
```Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY ./api ./api
COPY ./functions ./functions
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Deploy:
```bash
cd backend
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/backend-service

gcloud run deploy backend-service \
  --image gcr.io/YOUR_PROJECT_ID/backend-service \
  --platform managed \
  --allow-unauthenticated \
  --region YOUR_REGION
```

✅ Save the public URL output.

---

## 🔥 4. Firestore Setup

Initialize Firestore:
```bash
gcloud firestore databases create --region=YOUR_REGION
```

✅ Firestore will auto-scale as you store rows.

---

## 📂 5. Buckets for Datasets

Create raw bucket:
```bash
gsutil mb -p YOUR_PROJECT_ID -l YOUR_REGION gs://your-raw-bucket-name
```
Create results bucket:
```bash
gsutil mb -p YOUR_PROJECT_ID -l YOUR_REGION gs://your-results-bucket-name
```

✅ Allow backend service account to read/write both.

---

## ⚡ 6. Environment Variables

Set these in your backend code or Cloud Run env vars:

| Variable | Purpose |
|---|---|
| `RESULTS_BUCKET` | your-results-bucket-name |
| `RAW_BUCKET` | your-raw-bucket-name |


---

## 🛡️ 7. CORS and Security

Frontend → Backend (CORS): Already handled via FastAPI middleware.

Storage buckets → Allow Object Read (frontend bucket) + Read/Write (raw/results buckets) for backend.

Cloud Run → Expose only `/upload`, `/dataset`, `/rows`, `/export` routes.

---

## 🚀 8. Final Testing Checklist

- [ ] Upload CSV via frontend
- [ ] Evaluate via backend → Firestore
- [ ] Load dataset for review
- [ ] Patch category corrections
- [ ] Export corrected CSV to GCS
- [ ] Download final CSV

---

## 🎯 Bonus Automation (Optional)

Add a `cloudbuild.yaml` for automated Cloud Run deployment on git push.

---

# ✅ Congratulations!
You now have a full serverless, scalable, cloud-native Dataset Review App running 100% on Google Cloud! 🌎🚀