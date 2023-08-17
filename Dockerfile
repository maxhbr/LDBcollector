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
FROM node:latest as build

ARG APP_NAME=hermine
ARG APP_PATH=/opt/$APP_NAME

WORKDIR $APP_PATH

COPY package.json package-lock.json $APP_PATH/
RUN npm ci

COPY . $APP_PATH
RUN npm run build


FROM bitnami/python:3.10 as runtime

ARG APP_NAME=hermine
ARG APP_PATH=/opt/$APP_NAME
ARG POETRY_VERSION=1.4.1

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1
ENV \
    POETRY_VERSION=$POETRY_VERSION \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

WORKDIR $APP_PATH

# debug
RUN apt update && apt install -y postgresql-client net-tools

# install poetry and dependencies
RUN pip install "poetry==$POETRY_VERSION" gunicorn
COPY pyproject.toml poetry.lock $APP_PATH/
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --without dev

COPY hermine $APP_PATH/
# copy node modules
COPY --from=build $APP_PATH/hermine/vite_modules/dist $APP_PATH/vite_modules/dist

# COPY shared.json $APP_PATH/
COPY docker/docker-entrypoint.sh $APP_PATH/
COPY docker/docker_secrets.py $APP_PATH/hermine/mysecrets.py

EXPOSE $DJANGO_PORT

# init shared data
# RUN if [ -f shared.json ]; then $APP_PATH/manage.py init_shared_data shared.json; fi

# run entrypoint.sh
ENTRYPOINT /opt/hermine/docker-entrypoint.sh
