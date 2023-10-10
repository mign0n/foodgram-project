FROM python:3.9-slim
WORKDIR /app

COPY ../requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY .. .

WORKDIR foodgram
CMD ["gunicorn", "--bind", "0.0.0.0:9000", "foodgram.wsgi"]
