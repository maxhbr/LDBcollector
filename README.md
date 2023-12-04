<!-- SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>

     SPDX-License-Identifier: GPL-2.0-only
-->
# LicenseDb

License as a service provides a convenient and effective way for organizations to
manage their use of open-source licenses. With the growing popularity of open-source
software, organizations are finding it more difficult to keep track of the various
licenses and terms under which they are permitted to use open-source components.
Open-source licenses can be complicated, making it difficult to understand how they
apply to a specific piece of software or interact with other licenses. It can be
used for various purposes by organizations and tools like [FOSSology](https://fossology.org)
and [SW360](https://eclipse.org/sw360) like license identification, filtering, and
managing licenses. There are benefits of this service such as increasing flexibility,
a faster time-to-access, and managing the database.

## Database

Licensedb database has licenses, obligations, obligation map, users, their audits
and changes.

- **license_dbs** table has list of licenses and all the data related to the licenses.
- **obligations** table has the list of obligations that are related to the licenses.
- **obligation_maps** table that maps obligations to their respective licenses.
- **users** table has the user that are associated with the licenses.
- **audits** table has the data of audits that are done in obligations or licenses
- **change_logs** table has all the change history of a particular audit.

![alt text](./docs/assets/licensedb_erd.png)

### APIs

There are multiple API endpoints for licenses, obligations, user and audit
endpoints.

### API endpoints

| #   | Method    | API Endpoints                      | Examples                              | Descriptions                                                                          |
| --- | --------- | ---------------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------- |
| 1   | **GET**   | `/api/licenses/:shortname`         | /api/licenses/MIT                     | Gets all data related to licenses by their shortname                                  |
| 2   | **GET**   | `/api/licenses/`                   | /api/licenses/copyleft="t"&active="t" | Get filter the licenses as per the filters                                            |
| 3   | **POST**  | `/api/licenses`                    | /api/licenses                         | Create a license with unique shortname                                                |
| 4   | **POST**  | `/api/licenses/search`             | /api/licenses/search                  | Get the licenses with the post request filtered by field, search term and type       |
| 5   | **PATCH** | `/api/licenses/:shortname`         | /api/licenses/MIT                     | It updates the particular fields as requested of the license with shortname           |
| 6   | **GET**   | `/api/users`                       | /api/users                            | Get all the users and their data                                                      |
| 7   | **GET**   | `/api/users/:id`                   | /api/users/1                          | Get data relate to user by its id                                                     |
| 8   | **POST**  | `/api/users`                       | /api/users                            | Create a user with unique data                                                        |
| 9   | **GET**   | `/api/obligations`                 | /api/obligations                      | Get all the obligations                                                               |
| 10  | **GET**   | `/api/obligation/:topic`           | /api/obligation/topic                 | Gets all data related to obligations by their topic                                   |
| 11  | **POST**  | `/api/obligations`                 | /api/obligations                      | Create an obligation as well as add it to obligation map                              |
| 12  | **PATCH** | `/api/obligations/:topic`          | /api/obligations                      | It updates the particular fields as requested of the obligation with topic            |
| 13  | **GET**   | `/api/audit`                       | /api/audit                            | Get the audit history of all the licenses and obligations                             |
| 14  | **GET**   | `/api/audit/:audit_id`             | /api/audit/1                          | Get the data of a particular audit by its id                                          |
| 15  | **GET**   | `/api/audit/:audit_id/changes`     | /api/audit/1/changes                  | Get the change logs of the particular audit id                                        |
| 16  | **GET**   | `/api/audit/:audit_id/changes/:id` | /api/audit/1/changes/2                | Get a particular change log of the particular audit id                                |

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
