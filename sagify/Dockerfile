FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi pydantic==1.10.13 python-dotenv structlog uvicorn openai sagemaker Pillow anthropic

# Copy the rest of the application code into the container
COPY ./ /app/sagify/

# Expose port 8000
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "sagify.llm_gateway.main", "8000"]