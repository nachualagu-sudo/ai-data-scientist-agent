FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8010
WORKDIR /app
RUN addgroup --system app && adduser --system --ingroup app app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data/uploads data/charts data/models && chown -R app:app /app
USER app
EXPOSE 8010
CMD ["sh", "-c", "uvicorn FastAPI_Main_Server:app --host 0.0.0.0 --port ${PORT} --workers 1"]
