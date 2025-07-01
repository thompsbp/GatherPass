# Use an official Python runtime as a parent image.
FROM python:3.10-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy the dependency file first to leverage Docker's layer caching.
COPY requirements.txt .

# Install the Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the bot's source code into the container.
COPY . .

# The command to run when the container starts, executing the main bot script.
CMD ["python", "main.py"]
