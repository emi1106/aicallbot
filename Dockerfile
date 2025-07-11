# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Update the package list and install system dependencies
# This is the crucial step that fixes the errors.
# We use apt-get, the standard Debian package manager.
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    ffmpeg \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy the file that lists the Python dependencies
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Make port 8080 available to the world outside this container
ENV PORT 8080
EXPOSE 8080

# Define the command to run your app
CMD ["python", "main.py"]