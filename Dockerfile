FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY skills ./skills
COPY config ./config
RUN pip install --no-cache-dir .

ENV AGENT_TEAM_ALLOWED_ROOT=/workspace
EXPOSE 8008
CMD ["agent-team-api"]

