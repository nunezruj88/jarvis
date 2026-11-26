FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY portal/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --uid 10001 --no-create-home jarvis \
    && mkdir /data && chown jarvis /data
COPY portal/backend.py portal/bridge.py ./
COPY portal/static ./static
COPY public/style.css ./static/base.css
USER jarvis
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
