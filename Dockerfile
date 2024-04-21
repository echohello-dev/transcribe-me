FROM python:3.12-slim

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "/app/transcribe_me/main.py"]

LABEL org.opencontainers.image.source=https://github.com/echohello-dev/transcribe-me
LABEL org.opencontainers.image.description="The transcriber that uses Anthropic and OpenAI."
LABEL org.opencontainers.image.licenses=MIT