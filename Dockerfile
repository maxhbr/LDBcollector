# SPDX-FileCopyrightText: 2024 Kaushlendra Pratap <kaushlendra-pratap.singh@siemens.com>
# SPDX-License-Identifier: GPL-2.0-only
FROM golang:1.23 AS build

WORKDIR /LicenseDb

COPY go.mod go.sum ./
RUN go mod download

COPY cmd/ cmd/
COPY pkg/ pkg/

COPY external_ref_fields.example.yaml external_ref_fields.yaml

RUN wget https://raw.githubusercontent.com/fossology/fossology/master/install/db/licenseRef.json -O licenseRef.json
RUN wget -qO- https://github.com/golang-migrate/migrate/releases/latest/download/migrate.linux-amd64.tar.gz \
    | tar xvz -C /usr/local/bin && \
    chmod +x /usr/local/bin/migrate && \
    CGO_ENABLED=0 GOOS=linux go generate ./cmd/laas && \
    go build -a -o laas ./cmd/laas

RUN CGO_ENABLED=0 GOOS=linux go generate ./cmd/laas && go build -a -o laas ./cmd/laas

# Release Stage
FROM alpine:3.20 AS build-release

WORKDIR /app

RUN apk add --no-cache openssl bash libc6-compat postgresql-client\
    && addgroup -S noroot \
    && adduser -S noroot -G noroot

COPY entrypoint.sh /app/entrypoint.sh

COPY --from=build /LicenseDb/licenseRef.json /app/licenseRef.json
COPY --from=build /LicenseDb/laas /app/laas
COPY --from=build /usr/local/bin/migrate /usr/local/bin/migrate
COPY --from=build /LicenseDb/pkg /app/pkg

EXPOSE 8080

RUN chmod +rx /app/entrypoint.sh \
    && chmod +x /app/laas \
    && chown --recursive noroot:noroot /app

USER noroot:noroot

ENTRYPOINT [ "/app/entrypoint.sh" ]