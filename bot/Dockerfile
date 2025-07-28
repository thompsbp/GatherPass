# Use an official Python runtime as a parent image.
FROM python:3.10-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy the dependency file first to leverage Docker's layer caching.
COPY bot/requirements.txt .
COPY api_client ./api_client

# Install the Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the bot's source code into the container.
COPY bot/ .

# The command to run when the container starts, executing the main bot script.
CMD ["python", "main.py"]
