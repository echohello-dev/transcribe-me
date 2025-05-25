FROM python:3.12.8-slim-bullseye

RUN apt-get update && apt-get install -y build-essential ffmpeg curl

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "-m", "transcribe_me.main"]

LABEL org.opencontainers.image.source=https://github.com/echohello-dev/transcribe-me
LABEL org.opencontainers.image.description="The transcriber that uses Anthropic and OpenAI."
LABEL org.opencontainers.image.licenses=MIT