---
title: AI Travel Planner
emoji: ✈️
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# AI Travel Planner ✈️

AI-powered travel planning with itinerary generation and budget optimization.

## Features

- 🤖 AI-generated day-by-day travel itineraries (powered by Groq/Llama)
- 💰 Smart budget breakdown and optimization
- 🔐 User authentication with JWT
- 📊 Visual budget charts
- 🗺️ Multi-destination support

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL (Neon)
- **Frontend**: React + Vite
- **AI**: Groq API (Llama 3.3 70B)
- **Database**: Neon (serverless PostgreSQL)
- **Deployment**: Hugging Face Spaces (Docker)

## Environment Variables

Set these as **Repository Secrets** in HF Spaces Settings:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Neon PostgreSQL connection string (include `?sslmode=require`) |
| `GROQ_API_KEY` | API key from [console.groq.com](https://console.groq.com) |
| `JWT_SECRET` | Random secret string for JWT signing |

## Local Development

```bash
# Backend
cd backend
cp .env.example .env  # Fill in your values
uvicorn app.main:app --port 7860 --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Docker Build

```bash
docker build -t travelai .
docker run -p 7860:7860 --env-file backend/.env travelai
```

Visit [http://localhost:7860](http://localhost:7860)
