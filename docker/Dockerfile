FROM python:3.13-slim

WORKDIR /app
COPY backend /app/backend
COPY frontend /app/frontend
COPY data /app/data
RUN pip install --no-cache-dir fastapi uvicorn[standard] python-multipart pillow pydantic
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--app-dir", "/app/backend", "--host", "0.0.0.0", "--port", "8000"]