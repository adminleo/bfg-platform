FROM python:3.12-slim

WORKDIR /app

# Build context is repo root (../../), so paths are relative to bfg-platform/

# Install shared core package
COPY packages/core /tmp/bfg-core
RUN pip install --no-cache-dir /tmp/bfg-core && rm -rf /tmp/bfg-core

# Install SCIL app dependencies
COPY apps/scil/backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy SCIL backend code
COPY apps/scil/backend/ .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
