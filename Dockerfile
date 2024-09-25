FROM python:3.11-slim-bullseye
LABEL authors="ronylitv"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG UID=2000
ARG GID=2000

ENV UID=${UID}
ENV GID=${GID}

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gcc \
        musl-dev \
        sqlite3 \
    && groupadd -g $GID docker_user \
    && useradd -m -u $UID -g docker_user docker_user \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

USER docker_user

WORKDIR /home/docker_user/app

COPY --chown=docker_user:docker_user requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=docker_user:docker_user . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
