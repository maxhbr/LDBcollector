# TODO: still hacky and lots of things to fix

FROM haskell:latest AS builder
MAINTAINER Maximilian Huber <gh@maximilian-huber.de>
WORKDIR /LDBcollector
RUN set -x \
    && apt-get update \
    && apt-get install -y curl libcurl4-openssl-dev
COPY package.yaml stack.yaml stack.yaml.lock /LDBcollector/
RUN set -x \
    && mkdir -p app src test \
    && stack setup \
    && stack build --only-dependencies
COPY . /LDBcollector
RUN set -x \
    && stack build --ghc-options -j \
    && stack exec LDBcollector-exe priv

FROM node:14
WORKDIR /generated
RUN npm i -g markserv
COPY --from=builder /LDBcollector/_generated.priv /generated
ENTRYPOINT ["markserv", "/generated"]
