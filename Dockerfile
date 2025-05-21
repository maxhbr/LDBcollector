# SPDX-FileCopyrightText: 2024 Kaushlendra Pratap <kaushlendra-pratap.singh@siemens.com>
# SPDX-License-Identifier: GPL-2.0-only
FROM golang:1.23 AS build

WORKDIR /LicenseDb

COPY go.mod go.sum ./
RUN go mod download

COPY cmd/ cmd/
COPY pkg/ pkg/
COPY docs/ docs/
COPY external_ref_fields.example.yaml external_ref_fields.yaml

RUN wget https://raw.githubusercontent.com/fossology/fossology/master/install/db/licenseRef.json -O licenseRef.json

RUN CGO_ENABLED=0 GOOS=linux go generate ./cmd/laas && go build -a -o laas ./cmd/laas

# Release Stage
FROM alpine:3.20 AS build-release

WORKDIR /app

COPY entrypoint.sh /app/entrypoint.sh

RUN apk add --no-cache openssl bash libc6-compat \
    && addgroup -S noroot \
    && adduser -S noroot -G noroot

COPY --from=build /LicenseDb/licenseRef.json /app/licenseRef.json
COPY --from=build /LicenseDb/laas /app/laas

EXPOSE 8080

RUN chmod +rx /app/entrypoint.sh \
    && touch /app/.env \
    && chown --recursive noroot:noroot /app

USER noroot:noroot

ENTRYPOINT [ "/app/entrypoint.sh" ]
