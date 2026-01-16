# Portfolio Chatbot (RAG, My Data Only)

Public URL: https://my-portfolio-finalproject.onrender.com/

## screea shot
- home page
<img width="1166" height="915" alt="スクリーンショット 2026-01-15 16 09 22" src="https://github.com/user-attachments/assets/1afd3a29-6564-40ad-96ff-3b852cd5fe77" />

- chat page
<img width="1004" height="718" alt="スクリーンショット 2026-01-15 16 10 07" src="https://github.com/user-attachments/assets/b35c6bea-edec-47ae-aee8-c1f9ddcf1f52" />


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
