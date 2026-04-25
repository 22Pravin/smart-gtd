# Start with a lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy your requirements file first
COPY requirements.txt .

# Install the profilers and dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project files
COPY . .

# Keep the container running so we can interact with it
CMD ["tail", "-f", "/dev/null"]