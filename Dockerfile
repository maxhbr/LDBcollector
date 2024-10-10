# SPDX-FileCopyrightText: 2022 Hermine-team <hermine@inno3.fr>
#
# SPDX-License-Identifier: AGPL-3.0-only

# syntax=docker/dockerfile:1

# Helpers:
# https://github.com/bitnami/bitnami-docker-python
# https://stackoverflow.com/questions/53835198/integrating-python-poetry-with-docker
# https://bmaingret.github.io/blog/2021-11-15-Docker-and-Poetry

# Build vite modules on a separate image so we do not
# install node on the runtime image
FROM node:20 AS build

ARG BUILD_PATH=/opt/hermine

WORKDIR $BUILD_PATH

COPY package.json package-lock.json $BUILD_PATH/
RUN npm ci

COPY . $BUILD_PATH
RUN npm run build

FROM python:3.12-slim AS runtime

ARG INSTALL_PATH=/opt/hermine
ARG POETRY_VERSION=1.8.2
ARG GUNICORN_VERSION=22.0.0

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1
ENV \
    POETRY_VERSION=$POETRY_VERSION \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1
ENV \
    GUNICORN_VERSION=$GUNICORN_VERSION


WORKDIR $INSTALL_PATH

# debug
RUN apt-get update && apt-get install -y postgresql-client net-tools && rm -rf /var/lib/apt/lists/*

# install poetry and dependencies
ARG OPTIONAL_PIP_INSTALL=""
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" "gunicorn==$GUNICORN_VERSION" $OPTIONAL_PIP_INSTALL
COPY pyproject.toml poetry.lock $INSTALL_PATH/
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --without dev

COPY hermine $INSTALL_PATH/hermine
# copy node modules
COPY --from=build $INSTALL_PATH/hermine/vite_modules/dist $INSTALL_PATH/hermine/vite_modules/dist

COPY docker/docker-entrypoint.sh $INSTALL_PATH/
COPY docker/config.py $INSTALL_PATH/hermine/hermine/config.py

EXPOSE $DJANGO_PORT

# run entrypoint.sh
WORKDIR $INSTALL_PATH/hermine
ENTRYPOINT ["/opt/hermine/docker-entrypoint.sh"]
