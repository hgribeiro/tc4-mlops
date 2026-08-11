FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AUDIT_LOG_DIR=/tmp/responsible-next-step/decisions

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "responsible_next_step.api:app", "--host", "0.0.0.0", "--port", "8000"]
