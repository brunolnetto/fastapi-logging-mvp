# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory to /app
WORKDIR /app

RUN mkdir backend/

# Copy only the backend's requirements file into the container
COPY requirements.txt ./backend/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy the entire backend directory into /app/backend
COPY . ./backend/

# Expose the port that Uvicorn will run on
EXPOSE 8000

# Start the FastAPI app using Uvicorn
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
