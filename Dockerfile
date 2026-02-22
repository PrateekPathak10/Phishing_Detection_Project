# Use a lightweight Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy and install dependencies first to leverage Docker's build cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code and the pre-trained model
COPY . .

# Expose the port the Flask application runs on
EXPOSE 5000

# Command to run the Flask application using Gunicorn (production server)
# The format is module:variable
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]