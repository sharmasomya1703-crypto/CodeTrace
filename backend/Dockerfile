FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md* ./
COPY codetrace ./codetrace

RUN pip install --no-cache-dir .

ENV CODETRACE_ENABLE_EVAL=true
ENV CODETRACE_RUNNER=subprocess
ENV CODETRACE_CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://frontend:80

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/api/health || exit 1

CMD ["uvicorn", "codetrace.main:app", "--host", "0.0.0.0", "--port", "8000"]
