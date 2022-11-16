#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

FROM --platform=linux/amd64 python:3.8-slim-buster

# Python settings: Force unbuffered stdout and stderr (i.e. they are flushed to terminal immediately)
ENV PYTHONUNBUFFERED 1
# Python settings: do not write pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# OS requirements as per
# https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
       bzip2 \
       xz-utils \
       zlib1g \
       libxml2-dev \
       libxslt1-dev \
       libgomp1 \
       libsqlite3-0 \
       libgcrypt20 \
       libpopt0 \
       libzstd1 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create directory for scancode sources
WORKDIR /scancode-toolkit

# Copy sources into docker container
COPY ./scancode-toolkit /scancode-toolkit

# Run scancode once for initial configuration
RUN ./configure --clean && ./configure

# Add scancode to path
ENV PATH=/scancode-toolkit:$PATH

# --- Flask app ---

# Install java11
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
       openjdk-11-jre-headless \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy backend code
COPY ./backend/requirements.txt /backend/requirements.txt

# Install python deps
RUN pip install -r /backend/requirements.txt

COPY ./backend /backend

WORKDIR /backend

VOLUME [ "/backend/temp_files" ]

ENTRYPOINT ["flask", "run", "--port", "5000", "--host", "0.0.0.0"]

