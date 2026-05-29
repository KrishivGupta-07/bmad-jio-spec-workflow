FROM python:3.11-slim

# Install system dependencies, nodejs, and npm
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g @anthropic-ai/claude-code \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency definition and install
COPY pyproject.toml ./
# Create dummy app folder for pip install to succeed with cached dependencies
RUN mkdir app && touch app/__init__.py && pip install -e .

# Copy the rest of the backend files
COPY . .

# Expose port
EXPOSE 8000

# Run database migrations and start FastAPI backend
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
