FROM python:3.12-slim

WORKDIR /app

# Install Node.js for frontend build
RUN apt-get update && apt-get install -y curl ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Build frontend
COPY frontend/ frontend/
RUN cd frontend && npm ci && npm run build && \
    mkdir -p ../backend/static && \
    cp -r dist/* ../backend/static/ && \
    cd .. && rm -rf frontend/

# Copy backend code and data
COPY backend/ backend/
COPY data/ data/

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
