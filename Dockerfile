# Use a slim Python image
FROM python:3.11-slim

# --- Install Java (OpenJDK 17) ---
RUN apt-get update && apt-get install -y openjdk-17-jre curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables for Java
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# --- Set working directory inside the container ---
WORKDIR /app

# --- Copy all project files into the container ---
COPY . .

# --- Install Python dependencies ---
RUN pip install --no-cache-dir -r requirements.txt

# --- Expose the port FastAPI will run on ---
EXPOSE 8000

# --- Start the FastAPI server with Uvicorn ---
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
