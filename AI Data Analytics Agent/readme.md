# AI Data Analytics Agent (Ollama + Streamlit)

> Intelligent data analytics platform powered by local LLMs and Streamlit for comprehensive data analysis workflows

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=f## - **Ollama connection error:*## 👨‍💻 Author & License

All code and content in this repository is for educational and personal use.

**Somesh Ramesh Ghaturle**  
MS in Data Science, Pace University

📧 **Email:** [someshghaturle@gmail.com](mailto:someshghaturle@gmail.com)  
🐙 **GitHub:** [https://github.com/somesh-ghaturle](https://github.com/somesh-ghaturle)  
💼 **LinkedIn:** [https://www.linkedin.com/in/someshghaturle/](https://www.linkedin.com/in/someshghaturle/)

### 📄 MIT License

```
MIT License

Copyright (c) 2025 Somesh Ramesh Ghaturle

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
#!/usr/bin/env markdown
# AI Data Analytics Agent — Production README

This folder contains the AI Data Analytics Agent: a Streamlit UI wired to a local Ollama LLM-backed analytics engine. The instructions below show how to run the project in production using the provided Dockerfile and docker-compose manifest.

## Quick checklist (what this README covers)

- Build a production Docker image
- Start/stop the production service with `docker-compose`
- Required environment variables and defaults
- How uploads are handled (writable path inside container)
- Simple verification and troubleshooting steps

---

## Requirements

- Docker and docker-compose (or Docker Desktop)
- Ollama running on the Docker host and at a reachable URL (see `OLLAMA_HOST` below)

This project was developed for Python 3.11 and Streamlit, but when running via Docker you don't need a local Python installation.

---

## Recommended environment variables

- `OLLAMA_HOST` — URL for Ollama; default used in `docker-compose.production.yml` is `http://host.docker.internal:11434`. Set to the host that runs Ollama so the container can reach it.
- `OLLAMA_PREFERRED_MODEL` — optional. If set, the UI will prefer this model string when auto-initializing the analytics agent.
- `APP_UPLOAD_DIR` — optional. Directory inside the container where user uploads will be written. Default: `/tmp/app_uploads` (writable inside container). Do NOT point this to `/app/data` if you've mounted `./data:/app/data:ro`.

---

## Production: build and run (quick)

From the project root run:

```bash
cd "AI Data Analytics Agent"
# Build the production image (uses Dockerfile.production)
docker-compose -f docker-compose.production.yml build --no-cache

# Start the stack (detached)
docker-compose -f docker-compose.production.yml up -d

# Check container health and logs
docker ps --filter name=ai-data-analytics -a
docker logs --tail 200 <container_id>
```

To stop:

```bash
docker-compose -f docker-compose.production.yml down
```

Notes:

- The included compose file mounts `./data:/app/data:ro`. That mount is read-only by design so uploaded files must be written elsewhere inside the container (see `APP_UPLOAD_DIR` or `/tmp/app_uploads`).
- The production image is tagged as `somesh-ghaturle/ai-data-analytics:prod` in the compose file; change if you want a different name.

---

## Local development (optional)

- If you're developing locally and have Python set up, run the Streamlit app directly:

```bash
pip install -r requirements.txt
streamlit run web_ui.py
```

This will run the app on port 8501 by default.

---

## Verification & smoke tests

- A Playwright-based smoke test exists at `tests/ui_playwright_smoke.py`. It uploads a small CSV and saves `tests/ui_smoke_result.png`.
- In-container quick test (example):

```bash
docker exec <container_id> python3 -c "from analytics_core import OllamaAnalyticsAgent; print('import ok'); a=OllamaAnalyticsAgent(); print('model',a.model_name)"
```

---

## Troubleshooting

- Ollama unreachable: confirm `OLLAMA_HOST` points to a reachable host. For local Docker on macOS use `http://host.docker.internal:11434` (the compose file sets this by default).
- Read-only file errors: do not attempt to write to `/app/data` if it's mounted read-only. Use `/tmp/app_uploads` or set `APP_UPLOAD_DIR` to a writable path inside the container. To persist uploads, map a host directory to `/tmp/app_uploads` in `docker-compose.production.yml` (example below).
- Long LLM calls or timeouts: the analytics agent runs LLM calls inside a short worker timeout; if you see repeated timeouts, use a smaller model or increase Ollama resources.
- Port conflict on 8501: change the port mapping in `docker-compose.production.yml` or stop the conflicting service.

Example persistent upload mapping (edit `docker-compose.production.yml`):

```yaml
services:
  ai-data-analytics-agent:
    ...
    volumes:
      - ./data:/app/data:ro
      - ./uploads:/tmp/app_uploads # host directory for uploads (writable)
```

---

## Files of interest

- `web_ui.py` — Streamlit entrypoint (production UI)
- `analytics_core.py` — analytics engine and Ollama wrapper
- `Dockerfile.production` — production image build
- `docker-compose.production.yml` — compose manifest used for production runs

---

### Built with ❤️ using Streamlit, Ollama, and Python
