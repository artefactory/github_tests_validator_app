FROM python:3.9-slim-buster

ENV LANG=C.UTF-8 \
  LC_ALL=C.UTF-8

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  curl coreutils \
  && rm -rf /var/lib/apt/lists/*

RUN useradd -d /home/docker_user -m -s /bin/bash docker_user
USER docker_user

RUN mkdir -p /home/docker_user/workspace
WORKDIR /home/docker_user/workspace

# Install Poetry
RUN curl -sSL -o install-poetry.py https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py \
  && POETRY_HOME=/home/docker_user/poetry python install-poetry.py --preview \
  && rm install-poetry.py

ENV PATH="${PATH}:/home/docker_user/.poetry/bin:/home/docker_user/poetry/bin"

COPY pyproject.toml ./
COPY poetry.lock ./

RUN poetry install --no-root --only main

COPY . /home/docker_user/workspace/

CMD ["poetry", "run", "python3", "server.py"]
