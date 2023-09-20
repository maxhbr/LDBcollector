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

ARG BUILD_PATH=/opt/hermine

WORKDIR $BUILD_PATH

COPY package.json package-lock.json $BUILD_PATH/
RUN npm ci

COPY . $BUILD_PATH
RUN npm run build


FROM bitnami/python:3.10 as runtime

ARG INSTALL_PATH=/opt/hermine
ARG POETRY_VERSION=1.6.1

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1
ENV \
    POETRY_VERSION=$POETRY_VERSION \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

WORKDIR $INSTALL_PATH

# debug
RUN apt update && apt install -y postgresql-client net-tools

# install poetry and dependencies
RUN pip install "poetry==$POETRY_VERSION" gunicorn
COPY pyproject.toml poetry.lock $INSTALL_PATH/
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --without dev

COPY hermine $INSTALL_PATH/hermine
# copy node modules
COPY --from=build $INSTALL_PATH/hermine/vite_modules/dist $INSTALL_PATH/hermine/vite_modules/dist

# COPY shared.json $APP_PATH/
COPY docker/docker-entrypoint.sh $INSTALL_PATH/
COPY docker/config.py $INSTALL_PATH/hermine/hermine/config.py

EXPOSE $DJANGO_PORT

# init shared data
# RUN if [ -f shared.json ]; then $APP_PATH/manage.py init_shared_data shared.json; fi

# run entrypoint.sh
WORKDIR $INSTALL_PATH/hermine
ENTRYPOINT /opt/hermine/docker-entrypoint.sh
