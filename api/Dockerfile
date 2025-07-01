# Use an official Python runtime as a parent image.
# The 'slim' version is smaller and good for production.
FROM python:3.10-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the dependency file first to leverage Docker's layer caching.
# If requirements don't change, this layer will be reused, speeding up builds.
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's source code from the host into the container.
COPY . .

# The command to run when the container starts.
# It tells uvicorn to run the 'app' instance from the 'main.py' file.
# --host 0.0.0.0 makes the server accessible within the Docker network.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
