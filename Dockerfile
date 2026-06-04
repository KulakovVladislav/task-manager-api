FROM python:3.14-slim AS builder
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
RUN python -m venv /opt/venv
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

FROM python:3.14-slim AS runner
RUN useradd --system --shell /bin/false appuser
COPY --from=builder /opt/venv /opt/venv
WORKDIR /app
COPY entrypoint.sh .
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
ENV PATH="/opt/venv/bin:$PATH"
RUN chown -R appuser:appuser /app
USER appuser
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]