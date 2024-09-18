# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements.txt first, to leverage Docker's cache
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Install your package in editable mode
RUN pip install -e .

# Expose the port that Uvicorn will run on
EXPOSE 8000

# Run Uvicorn when the container launches
CMD ["uvicorn", "src.ai_clean_chat_backend.HTTPServer:app", "--host", "0.0.0.0", "--port", "8000"]
