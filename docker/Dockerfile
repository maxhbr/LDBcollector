# -*- mode: shell-script -*-

FROM phusion/baseimage:0.9.17

EXPOSE 80

CMD ["/sbin/my_init"]

RUN apt-get -y update && apt-get -y install add-apt-key # 2015-10-04

# nginx repository and GPG key
RUN add-apt-key --keyserver pool.sks-keyservers.net 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62

COPY nginx/sources.list     /etc/apt/sources.list.d/nginx.list

RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y install build-essential curl git libkyotocabinet-dev libraptor2-dev \
    nginx python-virtualenv python-pip php5-cli screen raptor2-utils scons

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /root
RUN git clone https://github.com/rdfhdt/hdt-cpp

RUN cd /root/hdt-cpp/libcds-v1.0.12 \
  && make \
  && cd /root/hdt-cpp/hdt-lib \
  && make tools

# gpg keys listed at https://github.com/iojs/io.js
RUN gpg --keyserver pool.sks-keyservers.net --recv-keys 9554F04D7259F04124DE6B476D5A82AC7E37093B DD8F2338BAE7501E3DD5AC78C273792F7D83545D

ENV IOJS_VERSION 3.3.1

RUN curl -SLO "https://iojs.org/dist/v$IOJS_VERSION/iojs-v$IOJS_VERSION-linux-x64.tar.gz" \
  && curl -SLO "https://iojs.org/dist/v$IOJS_VERSION/SHASUMS256.txt.asc" \
  && gpg --verify SHASUMS256.txt.asc \
  && grep " iojs-v$IOJS_VERSION-linux-x64.tar.gz\$" SHASUMS256.txt.asc | sha256sum -c - \
  && tar -xzf "iojs-v$IOJS_VERSION-linux-x64.tar.gz" -C /usr/local --strip-components=1 \
  && rm "iojs-v$IOJS_VERSION-linux-x64.tar.gz" SHASUMS256.txt.asc

WORKDIR /srv
RUN git clone https://gitlab.com/kuno/licensedb.git

WORKDIR /srv/licensedb
# RUN mkdir --parents node_modules
# WORKDIR /srv/licensedb/node_modules
# RUN git clone https://github.com/RubenVerborgh/HDT-Node hdt
# WORKDIR /srv/licensedb/node_modules/hdt
# RUN git checkout 90022554f11ead4cee92b960b4de43eebf72354c
# RUN git submodule init && git submodule update
# RUN npm install --unsafe-perm
# RUN npm test
# WORKDIR /srv/licensedb

ENV HOME /root

RUN ln -s /root/hdt-cpp/hdt-lib/tools/rdf2hdt bin/rdf2hdt
RUN bin/bootstrap.sh
RUN scons

RUN printf "\ndaemon off;\n" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/licensedb.org.conf  /etc/nginx/conf.d/licensedb.org.conf
COPY service/nginx.sh          /etc/service/nginx/run
COPY service/licensedb.sh      /etc/service/licensedb/run
COPY service/ldf.sh            /etc/service/ldf/run

