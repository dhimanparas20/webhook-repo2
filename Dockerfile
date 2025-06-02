# Use the smallest official Python runtime
FROM python:3.11.11-alpine

# Set environment variables for Python to optimize runtime and set timezone
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    COMPOSE_BAKE=true \
    TZ=Asia/Kolkata

# Copy the uv and uvx binaries from the official uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install tzdata to configure timezone and any build dependencies
RUN apk add --no-cache tzdata

# Set working directory
WORKDIR /app

# Copy only dependency files first for better Docker cache utilization
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy the entire application code into the container
COPY . .

# Expose port 5000 for the Flask application
EXPOSE 5000

# Run the Flask application with Gunicorn
CMD ["uv","run","gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "run:app"]