# Application image: Flask portal + sandbox backend (gunicorn).
FROM python:3.12-slim

# Docker CLI only (no daemon). The app talks to the HOST daemon through the
# mounted socket and starts one sibling container per logged-in user.
COPY --from=docker:27-cli /usr/local/bin/docker /usr/local/bin/docker

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencies first, so the layer cache survives source changes.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY sandbox ./sandbox

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=4)"]

# Worker count comes from WEB_CONCURRENCY, extra flags from GUNICORN_CMD_ARGS
# (see .env.example) - keep them out of this CMD to avoid precedence surprises.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--worker-class", "gthread", "--access-logfile", "-", "app:app"]
