# Use official Python runtime as a parent image
FROM python:3.10-slim

# Add a non-root user (Hugging Face Spaces runs as user 1000)
RUN useradd -m -u 1000 user

# Set working directory
WORKDIR /app

# Install system dependencies required by OpenCV and other libraries
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Change ownership of the app directory to the new user
RUN chown -R user:user /app

# Switch to the non-root user
USER user

# Ensure local bin is in PATH for pip installs
ENV PATH="/home/user/.local/bin:${PATH}"

# Copy requirements file first to leverage Docker cache
COPY --chown=user:user requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY --chown=user:user . .

# Set environment variables for Hugging Face Spaces compatibility
ENV CENTRAL_API_HOST=0.0.0.0
ENV CENTRAL_API_PORT=7860

# Expose port 7860
EXPOSE 7860

# Run the main runner script
CMD ["python", "main.py"]
