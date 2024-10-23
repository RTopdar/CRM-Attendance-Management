# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Pipfile and Pipfile.lock to the working directory
COPY Pipfile Pipfile.lock ./

# Install pipenv and the dependencies
RUN pip install pipenv && pipenv install --deploy --ignore-pipfile

# Copy the rest of the application code to the working directory
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Run the application
CMD ["pipenv", "run", "gunicorn", "--bind", "0.0.0.0:8080", "app:app"]