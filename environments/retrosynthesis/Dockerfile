FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml /app/pyproject.toml
COPY THIRD_PARTY_NOTICES.md /app/THIRD_PARTY_NOTICES.md
COPY src /app/src
RUN pip install --no-cache-dir '.[api]'
USER 10001:10001
EXPOSE 8080
CMD ["uvicorn", "synthesis_route_gym.api:app_from_environment", "--factory", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
