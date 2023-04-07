# FROM haskell:9.2.7
FROM fpco/stack-build:lts-20.17 as build

WORKDIR /workdir

COPY stack.yaml package.yaml stack.yaml.lock /workdir/
RUN stack build --system-ghc --dependencies-only

COPY CHANGELOG.md ldbcollector.cabal LICENSE README.org Setup.hs /workdir/
COPY app/ /workdir/app
COPY test/ /workdir/test
COPY src/ /workdir/src

RUN set -x \
 && stack build --system-ghc \
 && mv "$(stack path --local-install-root --system-ghc)/bin" /workdir/bin

FROM fpco/stack-build:lts-20.17 as run
EXPOSE 3000
WORKDIR /workdir
COPY --from=build /workdir/bin .
COPY data /workdir/data
CMD ["./ldbcollector-exe"]
