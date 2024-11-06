# Use an official Python runtime as a base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any necessary dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the app will run on (optional, depending on your app)
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]
