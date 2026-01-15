# Portfolio Chatbot (RAG, My Data Only)

Public URL: https://my-portfolio-finalproject.onrender.com/

## Overview
- Django-based portfolio site with a chat UI.
- Retrieval-augmented answers from my own documents only.
- Frontend is Django templates + Tailwind v4 CLI build.

## Tech Stack
- Backend: Django 6, Django REST Framework
- RAG: pgvector + PostgreSQL
- LLM/Embeddings: OpenAI API
- Frontend: Django templates, Tailwind CSS v4 CLI
- Security: reCAPTCHA v3
- Infra: Render (app), Neon (PostgreSQL)

## Local Dev (Quick)
```bash
python manage.py runserver
```

## Deploy
- App hosting: Render
- Database: Neon (PostgreSQL)
