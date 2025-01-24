FROM --platform=linux/amd64 python:3.9-slim-buster 

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
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/home/docker_user/.local/bin:$PATH"

COPY pyproject.toml ./
COPY poetry.lock ./

RUN poetry install --no-root --only main

COPY . /home/docker_user/workspace/

RUN poetry install --only main

CMD ["poetry", "run", "launch_github_app"]
