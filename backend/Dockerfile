FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only the dependency manifest first
COPY pyproject.toml ./

# Create a minimal src package stub so pip install -e . works without the real src
RUN mkdir -p app && touch app/__init__.py

# Install all dependencies (this layer is cached as long as pyproject.toml doesn't change)
RUN pip install --upgrade pip && pip install -e .

# Copy the full application code (changes here won't invalidate the dep cache above)
COPY . .

# Run the application
# HF Spaces routes external traffic to port 7860
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}