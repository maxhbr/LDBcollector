# -*- mode: shell-script -*-

# FROM ubuntu:14.04
FROM phusion/baseimage:0.9.16

CMD ["/sbin/my_init"]

RUN apt-get -y update && apt-get -y upgrade

RUN apt-get -y install apache2 build-essential curl git libkyotocabinet-dev libraptor2-dev \
    python-virtualenv python-pip php5-cli

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# gpg keys listed at https://github.com/iojs/io.js
RUN gpg --keyserver pool.sks-keyservers.net --recv-keys 9554F04D7259F04124DE6B476D5A82AC7E37093B DD8F2338BAE7501E3DD5AC78C273792F7D83545D

ENV IOJS_VERSION 1.4.1

RUN curl -SLO "https://iojs.org/dist/v$IOJS_VERSION/iojs-v$IOJS_VERSION-linux-x64.tar.gz" \
  && curl -SLO "https://iojs.org/dist/v$IOJS_VERSION/SHASUMS256.txt.asc" \
  && gpg --verify SHASUMS256.txt.asc \
  && grep " iojs-v$IOJS_VERSION-linux-x64.tar.gz\$" SHASUMS256.txt.asc | sha256sum -c - \
  && tar -xzf "iojs-v$IOJS_VERSION-linux-x64.tar.gz" -C /usr/local --strip-components=1 \
  && rm "iojs-v$IOJS_VERSION-linux-x64.tar.gz" SHASUMS256.txt.asc

WORKDIR /root
RUN git clone https://github.com/rdfhdt/hdt-cpp

RUN cd /root/hdt-cpp/libcds-v1.0.12 \
  && make \
  && cd /root/hdt-cpp/hdt-lib \
  && make tools

WORKDIR /srv
RUN git clone https://github.com/warpr/licensedb

WORKDIR /srv/licensedb
RUN ln -s /root/hdt-cpp/hdt-lib/tools/rdf2hdt bin/rdf2hdt
RUN bin/bootstrap.sh
RUN make

COPY service/apache2.sh          /etc/service/apache2/run
COPY apache2/licensedb.conf      /etc/apache2/sites-available/licensedb.conf
RUN a2dissite 000-default \
    && a2ensite licensedb

