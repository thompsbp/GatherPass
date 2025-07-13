# --- Base Stage ---
# This stage installs dependencies, which are common to both dev and prod.
# It's defined as 'base' so other stages can build from it.
FROM python:3.10-slim as base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Development Stage ---
# This stage is used when running with docker-compose.override.yml.
# It builds on 'base' and adds development-specific features.
FROM base as dev
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
# The CMD enables live reloading, which watches for file changes from the mounted volume.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# --- Production Stage ---
# This is the default stage used by the main docker-compose.yml.
# It also builds on 'base' but prepares a lean image for production.
FROM base as prod
# Copy the application code into the image. This is NOT done in dev, where we use a volume.
COPY . .
# The production CMD does NOT use --reload for better performance and stability.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
