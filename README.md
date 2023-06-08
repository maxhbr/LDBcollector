<!-- SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>

     SPDX-License-Identifier: GPL-2.0-only
-->
# LicenseDb

This project aims to create a centralized OSS license database, to manage opensource
licenses used by an organization. And different compliance tools like fossology,
sw360 etc. can sync with licenseDB application to update its own license data.

## Prerequisite

Please [install and set-up Golang](https://go.dev/doc/install) on your system
in advance.

## How to run this project?

- Clone this Project and Navigate to the folder.

``` bash
git clone https://github.com/fossology/LicenseDb.git
cd LicenseDb
```

- Build the project using following command.

```bash
go build ./cmd/laas
```

- Run the executable.

```bash
./laas
```

- You can directly run it by the following command.

```bash
go run ./cmd/laas
```
