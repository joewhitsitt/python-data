FROM python:3.9-slim

# Use UTF-8 by default
ENV PYTHONUTF8=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

# Copy the entrypoint script
COPY entrypoint.sh .

# Make the script executable
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]