# Use official Python base image
FROM python:3.13

RUN apt-get update && apt-get install -y libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev -y
# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
