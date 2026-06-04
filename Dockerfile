FROM python:3.14-slim AS builder
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
RUN python -m venv /opt/venv
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

FROM python:3.14-slim AS runner
RUN useradd --system -m --shell /bin/false appuser
COPY --from=builder /opt/venv /opt/venv
WORKDIR /app
COPY entrypoint.sh .
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
ENV PATH="/opt/venv/bin:$PATH"
RUN chmod +x entrypoint.sh && chown -R appuser:appuser /app
USER appuser
ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--log-level", "info", "--access-logfile", "-", "--error-logfile", "-"]
