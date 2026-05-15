FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive
ENV HF_HUB_DISABLE_PROGRESS_BARS=1
RUN apt-get update && apt-get install -y python3.10 python3-pip python3-venv curl && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
RUN ln -s /usr/bin/python3.10 /usr/bin/python
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN uv venv $VIRTUAL_ENV --python /usr/bin/python3.10
COPY requirements.txt .
RUN uv pip install --no-cache torch==2.8.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
RUN uv pip install --no-cache -r requirements.txt
COPY . .
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 16310 --no-access-log"]
