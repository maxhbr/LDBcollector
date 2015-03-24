# -*- mode: shell-script -*-

FROM phusion/baseimage:0.9.16
# FROM phusion/passenger-full:0.9.15

EXPOSE 80

CMD ["/sbin/my_init"]

RUN apt-get -y update && apt-get -y install add-apt-key

# nginx repository and GPG key
RUN add-apt-key --keyserver pool.sks-keyservers.net 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62

COPY nginx/sources.list     /etc/apt/sources.list.d/nginx.list

RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y install build-essential curl git libkyotocabinet-dev libraptor2-dev \
    nginx python-virtualenv python-pip php5-cli screen

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /root
RUN git clone https://github.com/rdfhdt/hdt-cpp

RUN cd /root/hdt-cpp/libcds-v1.0.12 \
  && make \
  && cd /root/hdt-cpp/hdt-lib \
  && make tools

# gpg keys listed at https://github.com/iojs/io.js
RUN gpg --keyserver pool.sks-keyservers.net --recv-keys 9554F04D7259F04124DE6B476D5A82AC7E37093B DD8F2338BAE7501E3DD5AC78C273792F7D83545D

ENV IOJS_VERSION 1.5.1

RUN curl -SLO "https://iojs.org/dist/v$IOJS_VERSION/iojs-v$IOJS_VERSION-linux-x64.tar.gz" \
  && curl -SLO "https://iojs.org/dist/v$IOJS_VERSION/SHASUMS256.txt.asc" \
  && gpg --verify SHASUMS256.txt.asc \
  && grep " iojs-v$IOJS_VERSION-linux-x64.tar.gz\$" SHASUMS256.txt.asc | sha256sum -c - \
  && tar -xzf "iojs-v$IOJS_VERSION-linux-x64.tar.gz" -C /usr/local --strip-components=1 \
  && rm "iojs-v$IOJS_VERSION-linux-x64.tar.gz" SHASUMS256.txt.asc

RUN printf "\ndaemon off;\n" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/licensedb.org.conf  /etc/nginx/conf.d/licensedb.org.conf
COPY service/nginx.sh          /etc/service/nginx/run
COPY service/licensedb.sh      /etc/service/licensedb/run
COPY service/ldf.sh            /etc/service/ldf/run

WORKDIR /srv
RUN git clone https://github.com/warpr/licensedb

WORKDIR /srv/licensedb
RUN ln -s /root/hdt-cpp/hdt-lib/tools/rdf2hdt bin/rdf2hdt
RUN bin/bootstrap.sh
# We need two passes because some of the targets to be built are not known during
# the first run.
RUN make && make

